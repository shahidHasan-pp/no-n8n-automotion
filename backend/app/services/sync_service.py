
import requests
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.utils.logger import get_logger
from app.models.enums import PlatformType
from datetime import datetime # Added datetime import

logger = get_logger("sync_service")

# This would be in a config file in a real application
EXTERNAL_API_URL = "http://quizard.com/getSyncUpdate" # Updated URL

class SyncService:
    def _get_platform_enum(self, platform_name: str) -> PlatformType:
        try:
            return PlatformType[platform_name.upper()]
        except KeyError:
            logger.warning(f"Invalid platform name '{platform_name}' found in payload. Skipping.")
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
                    continue

                try:
                    # 1. Check if user exists
                    user = crud.user.get_by_username(db, username=username)
                    user_in = schemas.UserCreate(
                        username=username,
                        phone_number=user_data.get("phone"),
                    )
                    
                    if user:
                        # 2. Update existing user
                        update_data = user_in.dict(exclude_unset=True)
                        crud.user.update(db, db_obj=user, obj_in=update_data)
                        logger.debug(f"Updated user: {username}")
                    else:
                        # 3. Create new user
                        user = crud.user.create(db, obj_in=user_in)
                        logger.info(f"Created new user: {username}")

                    # 4. Set platform registration flag
                    setattr(user, platform_enum.value, True)
                    db.add(user)
                    db.commit()

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
                    continue

                try:
                    # Parse dates
                    start_date_str = sub_data.get("start_date")
                    end_date_str = sub_data.get("end_date")
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S") if start_date_str else None
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S") if end_date_str else None

                    # 1. Sync Subscription
                    subscription = crud.subscription.get_by_name(db, name=sub_name)
                    if not subscription:
                        sub_in = schemas.SubscriptionCreate(name=sub_name, platform=platform_enum)
                        subscription = crud.subscription.create(db, obj_in=sub_in)
                        logger.info(f"Created new subscription: {sub_name} for platform {platform_name}")

                    # 2. Link User to Subscription
                    user = crud.user.get_by_username(db, username=username)
                    if not user:
                        logger.warning(f"Cannot link subscription: User '{username}' not found.")
                        continue
                    
                    existing_link = db.query(models.UserSubscribed).filter(
                        models.UserSubscribed.user_id == user.id,
                        models.UserSubscribed.subs_id == subscription.id
                    ).first()

                    if existing_link:
                        if start_date:
                            existing_link.start_date = start_date
                        if end_date:
                            existing_link.end_date = end_date
                        db.add(existing_link) # Mark as modified
                        db.commit() # Commit changes to existing link
                        logger.debug(f"Updated link dates for user {username} and subscription {sub_name}")
                    else:
                        link_in = schemas.UserSubscribedCreate(
                            user_id=user.id,
                            subs_id=subscription.id,
                            start_date=start_date,
                            end_date=end_date
                        )
                        crud.user_subscribed.create(db, obj_in=link_in)
                        db.commit() # Commit changes for new link
                        logger.info(f"Linked user {username} to subscription {sub_name} with dates {start_date}-{end_date}")

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
                score = played_item.get("right_cout") # Note the field name 'right_cout'
                time_taken = played_item.get("time_taken")
                played_time_str = played_item.get("time") # New field

                if not all([username, sub_name, score is not None, time_taken is not None, played_time_str]):
                    logger.warning(f"Skipping incomplete played record: {played_item}")
                    continue
                
                try:
                    played_time = datetime.strptime(played_time_str, "%Y-%m-%d %H:%M:%S")

                    user = crud.user.get_by_username(db, username=username)
                    subscription = crud.subscription.get_by_name(db, name=sub_name)

                    if not user:
                        logger.warning(f"Cannot record quiz: User '{username}' not found.")
                        continue
                    if not subscription:
                        logger.warning(f"Cannot record quiz: Subscription '{sub_name}' not found.")
                        continue
                        
                    quiz_in = schemas.PlayedQuizCreate(
                        user_id=user.id,
                        subs_id=subscription.id,
                        score=score,
                        time=time_taken,
                        created_at=played_time # Use the 'time' field for created_at
                    )
                    crud.quiz.create(db, obj_in=quiz_in)
                    db.commit() # Commit for new quiz record
                    logger.info(f"Recorded quiz for user {username}, subscription {sub_name}, score: {score} at {played_time}")

                except Exception as e:
                    logger.error(f"Error recording quiz for user '{username}' and sub '{sub_name}': {e}")
                    db.rollback()
        logger.info("Finished processing played quizzes.")

    def sync_from_updates_api(self, db: Session):
        logger.info(f"Starting synchronization from external API: {EXTERNAL_API_URL}")
        try:
            response = requests.get(EXTERNAL_API_URL, timeout=30)
            response.raise_for_status()
            payload = response.json()
            logger.info("Successfully fetched data from external API.")

            if "login" in payload:
                self._process_logins(db, payload["login"])
            
            if "subscription" in payload:
                self._process_subscriptions(db, payload["subscription"])

            if "played" in payload:
                self._process_played(db, payload["played"])

            logger.info("Synchronization process completed successfully.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data from external API: {e}")
            db.rollback() # Rollback in case of request exception
        except Exception as e:
            logger.error(f"An unexpected error occurred during synchronization: {e}")
            db.rollback()

sync_service = SyncService()
