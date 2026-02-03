
import requests
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.utils.logger import get_logger
from app.models.enums import PlatformType
from datetime import datetime # Added datetime import
from typing import Optional

logger = get_logger("sync_service")

# This should ideally be in app/core/config.py and loaded from environment variables
# For now, hardcoding the list of external API URLs
EXTERNAL_API_URLS = [
    #"http://quizard.com/getSyncUpdate",
    "http://127.0.0.1:8000/api/getSyncUpdate/",
    "https://arcaderush.xyz/api/manual/last30minutes"
]

class SyncService:
    def _get_platform_enum(self, platform_name: str) -> PlatformType:
        try:
            return PlatformType[platform_name.upper()]
        except KeyError:
            logger.warning(f"Invalid platform name '{platform_name}' found in payload. Skipping.")
            return None

    def formatDatetime(self, datetime_str: str) -> Optional[str]:
        if not datetime_str:
            return None
        # Normalize datetime string to use 'T' separator
        datetime_str = str(datetime_str).replace(" ", "T")
        try:
            dt = datetime.fromisoformat(datetime_str)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            logger.warning(f"Could not parse datetime string '{datetime_str}'")
            return None

    def _get_or_create_user(self, db: Session, username: str, platform_enum: PlatformType, phone: Optional[str] = None) -> Optional[models.User]:
        """Gets a user by username or creates a new one if not found."""
        if not username:
            logger.warning("Attempted to get or create a user with an empty username.")
            return None
        
        user = crud.user.get_by_username(db, username=username)
        if user:
            return user
        
        try:
            logger.info(f"User '{username}' not found. Creating new user.")
            user_in = schemas.UserCreate(username=username, phone_number=phone)
            user = crud.user.create(db, obj_in=user_in)
            setattr(user, platform_enum.value, True)
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Successfully created new user '{username}' from sync.")
            return user
        except Exception as e:
            logger.error(f"Error creating user '{username}' from sync: {e}")
            db.rollback()
            return None

    def _get_or_create_subscription(self, db: Session, sub_name: str, platform_enum: PlatformType) -> Optional[models.Subscription]:
        """Gets a subscription by name or creates a new one if not found."""
        if not sub_name:
            logger.warning("Attempted to get or create a subscription with an empty name.")
            return None
            
        subscription = crud.subscription.get_by_name(db, name=sub_name)
        if subscription:
            return subscription

        try:
            logger.info(f"Subscription '{sub_name}' not found. Creating new subscription.")
            sub_in = schemas.SubscriptionCreate(name=sub_name, platform=platform_enum)
            subscription = crud.subscription.create(db, obj_in=sub_in)
            db.commit()
            db.refresh(subscription)
            logger.info(f"Created new subscription '{sub_name}' for platform {platform_enum.name}.")
            return subscription
        except Exception as e:
            logger.error(f"Error creating subscription '{sub_name}' from sync: {e}")
            db.rollback()
            return None

    def _process_logins(self, db: Session, login_data: dict):
        logger.info("Processing logins...")
        for platform_name, users in login_data.items():
            platform_enum = self._get_platform_enum(platform_name)
            if not platform_enum:
                continue

            for user_data in users:
                username = user_data.get("username")
                if not username:
                    logger.warning("Skipping login record with empty username.")
                    continue

                user = crud.user.get_by_username(db, username=username)
                if user:
                    logger.debug(f"User '{username}' already exists, skipping creation.")
                    continue
                
                try:
                    # Create new user if it doesn't exist
                    user_in = schemas.UserCreate(
                        username=username,
                        phone_number=user_data.get("phone"),
                    )
                    new_user = crud.user.create(db, obj_in=user_in)
                    setattr(new_user, platform_enum.value, True)
                    db.add(new_user)
                    db.commit()
                    logger.info(f"Created new user via login sync: {username}")
                except Exception as e:
                    logger.error(f"Error processing login for user '{username}': {e}")
                    db.rollback()
        logger.info("Finished processing logins.")

    def _process_subscriptions(self, db: Session, subscription_data: dict):
        logger.info("Processing subscriptions...")
        for platform_name, subscriptions in subscription_data.items():
            platform_enum = self._get_platform_enum(platform_name)
            if not platform_enum:
                continue
            
            for sub_data in subscriptions:
                username = sub_data.get("username")
                sub_name = sub_data.get("service_type")
                if not (username and sub_name):
                    logger.warning(f"Skipping subscription record with missing username or service_type: {sub_data}")
                    continue

                try:
                    user = self._get_or_create_user(db, username, platform_enum, phone=sub_data.get("phone"))
                    if not user:
                        logger.warning(f"Could not get or create user '{username}', skipping subscription link.")
                        continue

                    subscription = self._get_or_create_subscription(db, sub_name, platform_enum)
                    if not subscription:
                        logger.warning(f"Could not get or create subscription '{sub_name}', skipping link for user '{username}'.")
                        continue

                    start_date = self.formatDatetime(sub_data.get("start_date"))
                    end_date = self.formatDatetime(sub_data.get("end_date"))
                    
                    existing_link = db.query(models.UserSubscribed).filter(
                        models.UserSubscribed.user_id == user.id,
                        models.UserSubscribed.subs_id == subscription.id
                    ).first()

                    if existing_link:
                        if start_date: existing_link.start_date = start_date
                        if end_date: existing_link.end_date = end_date
                        db.add(existing_link)
                        logger.debug(f"Updated subscription link for user '{username}' to '{sub_name}'.")
                    else:
                        link_in = schemas.UserSubscribedCreate(
                            user_id=user.id, subs_id=subscription.id,
                            start_date=start_date, end_date=end_date
                        )
                        crud.user_subscribed.create(db, obj_in=link_in)
                        logger.info(f"Linked user '{username}' to subscription '{sub_name}'.")

                    db.commit()
                except Exception as e:
                    logger.error(f"Error processing subscription for user '{username}' and sub '{sub_name}': {e}")
                    db.rollback()
        logger.info("Finished processing subscriptions.")

    def _process_played(self, db: Session, played_data: dict):
        logger.info("Processing played quizzes...")
        for platform_name, played_list in played_data.items():
            platform_enum = self._get_platform_enum(platform_name)
            if not platform_enum:
                continue

            for played_item in played_list:
                username = played_item.get("username")
                sub_name = played_item.get("service_type")
                score = played_item.get("right_cout")
                time_taken = played_item.get("time_taken")
                played_time_str = played_item.get("time")

                if not all([username, sub_name, score is not None, time_taken is not None, played_time_str]):
                    logger.warning(f"Skipping incomplete played record: {played_item}")
                    continue
                
                try:
                    user = self._get_or_create_user(db, username, platform_enum)
                    if not user:
                        logger.warning(f"Could not find or create user '{username}', skipping played record.")
                        continue
                        
                    subscription = self._get_or_create_subscription(db, sub_name, platform_enum)
                    if not subscription:
                        logger.warning(f"Could not find or create subscription '{sub_name}', skipping played record for user '{username}'.")
                        continue

                    played_time = self.formatDatetime(played_time_str)
                    if not played_time:
                        logger.warning(f"Could not parse played time for record: {played_item}. Skipping.")
                        continue
                        
                    quiz_in = schemas.PlayedQuizCreate(
                        user_id=user.id, subs_id=subscription.id,
                        score=score, time=time_taken, created_at=played_time
                    )
                    crud.quiz.create(db, obj_in=quiz_in)
                    db.commit()
                    logger.info(f"Recorded quiz for user '{username}', sub '{sub_name}', score: {score}")

                except Exception as e:
                    logger.error(f"Error recording quiz for user '{username}' and sub '{sub_name}': {e}")
                    db.rollback()
        logger.info("Finished processing played quizzes.")

    def sync_from_updates_api(self, db: Session):
        logger.info(f"Starting synchronization from external APIs: {EXTERNAL_API_URLS}")
        
        aggregated_payload = {"login": {}, "subscription": {}, "played": {}}

        for api_url in EXTERNAL_API_URLS:
            try:
                response = requests.get(api_url, timeout=30)
                response.raise_for_status()
                payload = response.json()
                logger.info(f"Successfully fetched data from {api_url}.")

                for category in ["login", "subscription", "played"]:
                    if category in payload:
                        for platform_name, data_list in payload[category].items():
                            if platform_name not in aggregated_payload[category]:
                                aggregated_payload[category][platform_name] = []
                            aggregated_payload[category][platform_name].extend(data_list)

            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch data from external API {api_url}: {e}")
                # Do not rollback entire transaction here, try next API
            except Exception as e:
                logger.error(f"An unexpected error occurred while fetching from {api_url}: {e}")
                # Do not rollback entire transaction here, try next API
        
        # Only process if any data was successfully aggregated
        if any(aggregated_payload[cat] for cat in aggregated_payload):
            try:
                if "login" in aggregated_payload:
                    self._process_logins(db, aggregated_payload["login"])
                
                if "subscription" in aggregated_payload:
                    self._process_subscriptions(db, aggregated_payload["subscription"])

                if "played" in aggregated_payload:
                    self._process_played(db, aggregated_payload["played"])

                logger.info("Synchronization process completed successfully for all aggregated data.")
            except Exception as e:
                logger.error(f"An error occurred during processing aggregated data: {e}")
                db.rollback() # Rollback if processing of aggregated data fails
        else:
            logger.info("No data fetched from any external API. Skipping processing.")

sync_service = SyncService()
