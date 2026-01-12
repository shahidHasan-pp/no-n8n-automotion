from typing import Dict, Optional, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.enums import MessengerType, NotificationContextType, MessageScenarioType, PlatformType
from app.models.user import User
from app.models.quiz import PlayedQuiz, UserSubscribed
from app.models.subscription import Subscription
from app.core.config import settings
from app.crud import message as message_crud
from app.schemas.messenger import MessageCreate
from app.utils.logger import get_logger

from .strategies.base import MessagingStrategy
from .strategies.email import EmailStrategy
from .strategies.whatsapp import WhatsappStrategy
from .strategies.telegram import TelegramStrategy
from .strategies.discord import DiscordStrategy

logger = get_logger(__name__)

class MessagingService:
    def __init__(self):
        self._strategies: Dict[MessengerType, MessagingStrategy] = {
            MessengerType.MAIL: EmailStrategy(),
            MessengerType.WHATSAPP: WhatsappStrategy(),
            MessengerType.TELEGRAM: TelegramStrategy(),
            MessengerType.DISCORD: DiscordStrategy(),
        }

    def send_message(self, db: Session, messenger_type: MessengerType, to: str, text: str, link: str = None, user_id: int = None) -> bool:
        
        extra_data = {}
        target = to

        # If we have a user_id, try to fetch better contact info from Messenger profile
        if user_id:
            from app.models.user import User as UserModel
            # Eager load messenger
            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            if user and user.messenger:
                msg_profile = user.messenger
                
                if messenger_type == MessengerType.TELEGRAM:
                    # Expect lookup in 'telegram' JSON column: {"chat_id": 123}
                    if msg_profile.telegram and isinstance(msg_profile.telegram, dict):
                        chat_id = msg_profile.telegram.get("chat_id")
                        if chat_id:
                            target = str(chat_id)
                            
                elif messenger_type == MessengerType.DISCORD:
                    # Expect lookup in 'discord' JSON column: {"dm_channel_id": "...", "user_id": "..."}
                    if msg_profile.discord and isinstance(msg_profile.discord, dict):
                        dm_channel_id = msg_profile.discord.get("dm_channel_id")
                        discord_user_id = msg_profile.discord.get("user_id")
                        
                        if dm_channel_id:
                            target = str(dm_channel_id)
                        
                        if discord_user_id:
                            extra_data['user_id'] = str(discord_user_id)
                            extra_data['create_dm'] = True
                            
                elif messenger_type == MessengerType.WHATSAPP:
                    # Validating phone from profile if needed, but usually 'to' from user.phone_number is fine
                    if msg_profile.whatsapp and isinstance(msg_profile.whatsapp, dict):
                        phone = msg_profile.whatsapp.get("phone")
                        if phone:
                            target = phone

        strategy = self._strategies.get(messenger_type)
        if not strategy:
            logger.error(f"No strategy found for {messenger_type}")
            return False
            
        success = strategy.send(target, text, link, extra_data=extra_data)
        
        # Log to DB via CRUD
        try:
            msg_data = MessageCreate(
                text=text,
                link=link,
                messenger_type=messenger_type,
                user_id=user_id
            )
            message_crud.create(db, obj_in=msg_data)
        except Exception as e:
            logger.error(f"Failed to log message to DB: {e}")
            
        return success

    def preview_contextual_messages(self, db: Session, context_type: NotificationContextType, subscription_id: Optional[int] = None) -> dict:
        """
        Preview what the message would look like for a given context.
        Returns a draft message and targeting info.
        """
        draft = ""
        target_summary = ""
        package_name = "Global"
        if subscription_id:
            sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
            if sub:
                package_name = sub.name

        if context_type == NotificationContextType.TOP_RANKERS:
            draft = f"🏆 Congratulations! You are among the top rankers in {package_name}! Your total score is {{total_score}}."
            query = db.query(User.username).join(PlayedQuiz, User.id == PlayedQuiz.user_id)
            if subscription_id:
                query = query.filter(PlayedQuiz.subs_id == subscription_id)
            top_players = query.group_by(User.id).order_by(func.sum(PlayedQuiz.score).desc()).limit(3).all()
            names = ", ".join([p.username for p in top_players])
            target_summary = f"Targets top 3 players: {names}"

        elif context_type == NotificationContextType.INSPIRING_TOP_10_30:
            draft = f"Keep pushing! You're currently ranked in the top 30 for {package_name} with {{total_score}} points. You can do it!"
            target_summary = "Targets players ranked 10-30 on the leaderboard."

        elif context_type == NotificationContextType.SOFT_REMINDER:
            draft = f"👋 Don't forget to play your {package_name} quizzes today! Your streak is at risk."
            target_summary = "Targets all subscribed users who haven't played today."

        elif context_type == NotificationContextType.CHANNEL_PROMO:
            draft = f"🚀 Unlock more rewards! Subscribe to our {package_name if subscription_id else 'premium'} packages for exclusive tournaments."
            target_summary = "Broadcast to the configured community channel."

        elif context_type == NotificationContextType.CHANNEL_CONGRATS_TOP_5:
            query = db.query(User.username).join(PlayedQuiz, User.id == PlayedQuiz.user_id)
            if subscription_id:
                query = query.filter(PlayedQuiz.subs_id == subscription_id)
            top_5 = query.group_by(User.id).order_by(func.sum(PlayedQuiz.score).desc()).limit(5).all()
            names = ", ".join([f"@{p.username}" for p in top_5])
            draft = f"🎉 Huge congratulations to our Top 5 players in {package_name}: {names}! Amazing job! 🥳"
            target_summary = "Broadcast to the configured community channel."

        return {
            "draft": draft,
            "target_summary": target_summary,
            "context_type": context_type
        }

    def send_contextual_messages(self, db: Session, context_type: NotificationContextType, messenger_type: MessengerType, subscription_id: Optional[int] = None, custom_text: Optional[str] = None) -> dict:
        """
        Send messages based on specific user activities and context.
        Allows custom_text override from frontend.
        """
        count = 0
        package_name = "Global"
        if subscription_id:
            sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
            if sub:
                package_name = sub.name
        
        if context_type == NotificationContextType.TOP_RANKERS:
            query = db.query(User.id, User.username, func.sum(PlayedQuiz.score).label('total_score'))\
                .join(PlayedQuiz, User.id == PlayedQuiz.user_id)
            
            if subscription_id:
                query = query.filter(PlayedQuiz.subs_id == subscription_id)
            
            top_players = query.group_by(User.id).order_by(func.sum(PlayedQuiz.score).desc()).limit(3).all()
            
            for i, p in enumerate(top_players):
                if custom_text:
                    text = custom_text.replace("{total_score}", str(p.total_score))\
                                     .replace("{username}", p.username)\
                                     .replace("{package_name}", package_name)
                else:
                    messages = [
                        "🏆 Congratulations! You are among the top rankers!",
                        "🔥 Incredible performance! You're dominating the leaderboard.",
                        "⭐ Keep it up! You are in the top 3!"
                    ]
                    msg_template = messages[i if i < len(messages) else 0]
                    text = f"{msg_template} in {package_name}. Your total score is {p.total_score}."
                
                self.send_message(db, messenger_type, "resolve_from_user_id", text, user_id=p.id)
                count += 1

        elif context_type == NotificationContextType.INSPIRING_TOP_10_30:
            sub_query = db.query(User.id, User.username, func.sum(PlayedQuiz.score).label('total_score'))\
                .join(PlayedQuiz, User.id == PlayedQuiz.user_id)
            if subscription_id:
                sub_query = sub_query.filter(PlayedQuiz.subs_id == subscription_id)
            
            targets = sub_query.group_by(User.id).order_by(func.sum(PlayedQuiz.score).desc()).offset(9).limit(21).all()
            
            for p in targets:
                if custom_text:
                    text = custom_text.replace("{total_score}", str(p.total_score))\
                                     .replace("{username}", p.username)\
                                     .replace("{package_name}", package_name)
                else:
                    text = f"Keep pushing in {package_name}! You're currently ranked in the top 30 with {p.total_score} points. You can do it!"
                self.send_message(db, messenger_type, "resolve_from_user_id", text, user_id=p.id)
                count += 1

        elif context_type == NotificationContextType.SOFT_REMINDER:
            sub_users_query = db.query(User.id).join(UserSubscribed, User.id == UserSubscribed.user_id)
            if subscription_id:
                sub_users_query = sub_users_query.filter(UserSubscribed.subs_id == subscription_id)
            
            played_today = db.query(PlayedQuiz.user_id).filter(func.date(PlayedQuiz.created_at) == date.today()).subquery()
            users_to_remind = sub_users_query.filter(User.id.notin_(played_today)).all()
            
            for u in users_to_remind:
                text = custom_text if custom_text else f"👋 Don't forget to play your {package_name} quizzes today! Your streak is at risk."
                if text and "{package_name}" in text:
                    text = text.replace("{package_name}", package_name)
                link = "https://yourplaylink.com" 
                self.send_message(db, messenger_type, "resolve_from_user_id", text, link=link, user_id=u.id)
                count += 1

        elif context_type == NotificationContextType.CHANNEL_PROMO:
            target = settings.TELEGRAM_CHANNEL_ID if messenger_type == MessengerType.TELEGRAM else None
            if target:
                text = custom_text if custom_text else f"🚀 Unlock more rewards! Subscribe to our {package_name if subscription_id else 'premium'} packages."
                if text and "{package_name}" in text:
                    text = text.replace("{package_name}", package_name)
                self.send_message(db, messenger_type, target, text, link="https://subscribe-here.com")
                count = 1

        elif context_type == NotificationContextType.CHANNEL_CONGRATS_TOP_5:
            target = settings.TELEGRAM_CHANNEL_ID if messenger_type == MessengerType.TELEGRAM else None
            if target:
                if custom_text:
                    text = custom_text.replace("{package_name}", package_name)
                else:
                    query = db.query(User.username).join(PlayedQuiz, User.id == PlayedQuiz.user_id)
                    if subscription_id:
                        query = query.filter(PlayedQuiz.subs_id == subscription_id)
                    top_5 = query.group_by(User.id).order_by(func.sum(PlayedQuiz.score).desc()).limit(5).all()
                    names = ", ".join([f"@{p.username}" for p in top_5])
                    text = f"🎉 Huge congratulations to our Top 5 players in {package_name}: {names}! Amazing job! 🥳"
                
                self.send_message(db, messenger_type, target, text)
                count = 1

        return {"status": "success", "processed_count": count}

    def send_scenario_messages(self, db: Session, scenario_type: MessageScenarioType, messenger_type: MessengerType) -> dict:
        """
        Send messages based on specific business scenarios.
        """
        import requests
        from datetime import timedelta
        count = 0

        # 1. Unsubscribed Reminder
        if scenario_type == MessageScenarioType.UNSUBSCRIBED_REMINDER:
            # Mapping from platform attribute name to PlatformType enum and display name
            platform_info = {
                "quizard": (PlatformType.QUIZARD, "কুইজার্ড"),
                "wordly": (PlatformType.WORDLY, "ওয়ার্ডলি"),
                "arcaderush": (PlatformType.ARCADERUSH, "আরকেড রাস"),
            }

            all_users = db.query(User).all()
            
            for user in all_users:
                days_since = (date.today() - user.created_at.date()).days
                if not (days_since > 0):
                    continue

                # 1. Find platforms the user is registered for
                registered_platforms = set()
                for platform_attr, (platform_enum, _) in platform_info.items():
                    if getattr(user, platform_attr, False):
                        registered_platforms.add(platform_enum)
                
                if not registered_platforms:
                    continue

                # 2. Find platforms the user has an active subscription for
                subscribed_platforms = set()
                user_subs = db.query(Subscription.platform)\
                    .join(UserSubscribed, Subscription.id == UserSubscribed.subs_id)\
                    .filter(UserSubscribed.user_id == user.id)\
                    .filter(UserSubscribed.end_date >= date.today()) \
                    .distinct().all()
                
                for sub in user_subs:
                    subscribed_platforms.add(sub.platform)

                # 3. Find platforms to remind the user about
                platforms_to_remind = registered_platforms - subscribed_platforms
                
                # 4. Send messages
                for platform_enum in platforms_to_remind:
                    # Look up the platform display name from the original platform_info dict
                    platform_display_name = ""
                    for key, (enum_val, display_name) in platform_info.items():
                        if enum_val == platform_enum:
                            platform_display_name = display_name
                            break
                    
                    if platform_display_name:
                        text = f"আপনি এখনো {platform_display_name} সার্ভিসেটিতে সাবস্ক্রিপশন করেন নি। এখনই সাবস্ক্রিপশন খেলুন এবং লুফে নিন ডেইলি, উইকলি, মেগা প্রাইজ সহ অনেক অনেক আকর্ষণীয় পুরষ্কার জেতার সুযোগ।"
                        self.send_message(db, messenger_type, "resolve", text, user_id=user.id)
                        count += 1
        # 2. Score Summary (after 2 rounds)
        elif scenario_type == MessageScenarioType.DAILY_SCORE_UPDATE:
            today = date.today()
            # Calculate users who played the same subscription at least 2 times today
            round_counts = db.query(
                PlayedQuiz.user_id,
                PlayedQuiz.subs_id,
                func.max(PlayedQuiz.score).label('max_score')
            ).filter(func.date(PlayedQuiz.created_at) == today)\
             .group_by(PlayedQuiz.user_id, PlayedQuiz.subs_id)\
             .having(func.count(PlayedQuiz.id) >= 2).all()
            
            for r in round_counts:
                # Get max score
                max_score = r.max_score
                if max_score is None:
                    continue
                    
                text = f"আপনার আজকের দুটি রাউন্ড সফল ভাবে সম্পন্ন হয়েছে। আজকে আপনার সর্বোচ্চ স্কোর “ {max_score} “"
                self.send_message(db, messenger_type, "resolve", text, user_id=r.user_id)
                count += 1

        # 3. 10 PM Rank Status
        elif scenario_type == MessageScenarioType.EVE_SCORE_RANKING:
            # Scenario 3: Targets users who played today. Shows rank from external leaderboard.
            leaderboard_urls = {
                # Quizard
                "Ramadan Quiz Challenge": "https://cms.quizard.live/api/leaderboard/?portal=15&event_id=34",
                "Sports Quiz Arena": "https://cms.quizard.live/api/leaderboard/?portal=15&event_id=75",
                "Brain Power Quiz": "https://cms.quizard.live/api/leaderboard/?portal=15&event_id=149",
                "Eid Mega Tournament Quiz": "https://cms.quizard.live/api/leaderboard/?portal=15&event_id=150",
                # Wordly
                "Wordly English": "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=67",
                "Wordly Bangla": "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=79",
                "Spelling Bee": "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=134",
                "Memory Match": "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=151",
                "Sudoku Easy": "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=152",
                "Sudoku Medium": "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=153",
                "SudokuHard": "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=154",
                "Sudoku Expert": "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=155",
                # Arcaderush
                "Moto Race City": "https://arcaderush.xyz/Leaderboard/GetLeaderboard?gameName=Knife%20Madness&eventId=1001",
                "Knife Madness": "https://arcaderush.xyz/Leaderboard/GetLeaderboard?gameName=Knife%20Madness&eventId=1002",
                "20248 Crazy Merge": "https://arcaderush.xyz/Leaderboard/GetLeaderboard?gameName=Knife%20Madness&eventId=1003",
            }
            
            # Helper to fetch rank (Duplicated or should be shared, but keeping inline for safety in replacement)
            def get_leaderboard_data(url: str):
                # response = requests.get(url, timeout=10)
                # response.raise_for_status()
                # return response.json()
                all_mock_data = {
                    "https://cms.quizard.live/api/leaderboard/?portal=15&event_id=149": [
                        {"User_Rank": 12, "msisdn": "1962401320", "score": 57, "time_taken": 136, "round_number": 1, "date": "2026-01-12", "event_id": 149, "category": None, "win": 1, "name": "", "username": "1962401320", "avatar_id": None, "avatar_img": ""},
                    ],
                    "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=149": [
                         {"User_Rank": 1, "msisdn": "1962401320", "score": 59, "time_taken": 136, "round_number": 1, "date": "2026-01-07", "event_id": 149, "category": None, "win": 1, "name": "", "username": "1962401320", "avatar_id": None, "avatar_img": ""},
                    ],
                    "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=151": [
                        {"User_Rank": 2, "msisdn": "1628975383", "score": 49, "time_taken": 156, "round_number": 1, "date": "2026-01-07", "event_id": 151, "category": None, "win": 1, "name": "Ullah", "username": "1628975383", "avatar_id": 1, "avatar_img": "images/20250417_180333.jpg"},
                    ],
                }
                return all_mock_data.get(url, [])

            today = date.today()
            # Get users who played today and their max score
            played_stats = db.query(
                PlayedQuiz.user_id,
                PlayedQuiz.subs_id,
                func.max(PlayedQuiz.score).label('max_score')
            ).filter(func.date(PlayedQuiz.created_at) == today)\
             .group_by(PlayedQuiz.user_id, PlayedQuiz.subs_id).all()

            for ps in played_stats:
                user = db.query(User).filter(User.id == ps.user_id).first()
                sub = db.query(Subscription).filter(Subscription.id == ps.subs_id).first()
                
                if not (user and sub and sub.name in leaderboard_urls):
                    continue

                game_name = sub.name
                max_score = ps.max_score
                url = leaderboard_urls[game_name]
                
                try:
                    data = get_leaderboard_data(url)
                    rank = None
                    
                    if "arcaderush.xyz" in url:
                        if isinstance(data, list):
                            for i, entry in enumerate(data):
                                if entry.get("username") == user.username:
                                    rank = i + 1
                                    break
                    else:
                        if isinstance(data, list):
                            for entry in data:
                                # Match username with msisdn (handling 0 prefix if needed)
                                msisdn = str(entry.get("msisdn", ""))
                                if msisdn == user.username or (user.username and msisdn == user.username.lstrip('0')) or (user.username and msisdn.lstrip('0') == user.username):
                                    rank = entry.get("User_Rank")
                                    break
                    
                    if rank:
                        text = f"আজকে আপনি “ {game_name} “ গেমটি খেলেছেন এবং এখন পর্যন্ত আপনার সর্বোচ্চ স্কোর “ {max_score} “। আপনি লিডারবোর্ডে “ {rank} “ তম অবস্থানে রয়েছেন।"
                        self.send_message(db, messenger_type, "resolve", text, user_id=user.id)
                        count += 1
                        
                except Exception as e:
                    logger.error(f"Error in EVE_SCORE_RANKING for {game_name}: {e}")
                    continue

        # 4. Expiry Reminder (last_date = today)
        elif scenario_type == MessageScenarioType.SUBSCRIPTION_EXPIRY:
            # Scenario 4: end_date == today
            expiring = db.query(UserSubscribed).filter(func.date(UserSubscribed.end_date) == date.today()).all()
            for es in expiring:
                sub = db.query(Subscription).filter(Subscription.id == es.subs_id).first()
                sub_name = sub.name if sub else "সার্ভিস"
                text = f"আগামী কাল আপনার “{sub_name}” সাবস্ক্রিপশনটি রিনিউ হবে। কোন রকম ব্যাঘাত ছাড়া নিয়মিত খেলে প্রাইজ পেতে অবশ্যই কাল বিকাশে যথেষ্ট ব্যালান্স রাখুন। ধন্যবাদ।"
                self.send_message(db, messenger_type, "resolve", text, user_id=es.user_id)
                count += 1

        # Inactive Subscriber (last_played_date < today - 3 days)
        elif scenario_type == MessageScenarioType.INACTIVE_SUBSCRIBER:
            # Scenario 5: Subscribed but stopped playing for consecutive 3 days.
            three_days_ago = date.today() - timedelta(days=3)
            # Users with active subscriptions
            active_subs = db.query(UserSubscribed.user_id).distinct().subquery()
            # Users who played in last 3 days
            played_recently = db.query(PlayedQuiz.user_id).filter(func.date(PlayedQuiz.created_at) >= three_days_ago).distinct().subquery()
            
            inactive_users = db.query(User).filter(User.id.in_(active_subs)).filter(User.id.notin_(played_recently)).all()
            for u in inactive_users:
                text = "আমরা লক্ষ্ করেছি বিগত তিন দিন যাবত আপনি কোন গেম খেলছেন না। নিয়মিত ডেইলি প্রাইজ গুলো জিততে আজ থেকেই আবার খেলা শুরু করুন। আপনার জন্য শুভকামনা।"
                self.send_message(db, messenger_type, "resolve", text, user_id=u.id)
                count += 1

        # 6. 10 AM Daily Reminder
        elif scenario_type == MessageScenarioType.DAILY_PLAY_REMINDER:
            # Scenario 6: 10 AM reminder to subscribed users who didn't play today.
            today = date.today()
            active_subs = db.query(UserSubscribed.user_id).distinct().subquery()
            played_today = db.query(PlayedQuiz.user_id).filter(func.date(PlayedQuiz.created_at) == today).distinct().subquery()
            
            to_remind = db.query(User).filter(User.id.in_(active_subs)).filter(User.id.notin_(played_today)).all()
            for u in to_remind:
                text = "খেলার সময় চলছে। ডেইলি প্রাইজ পেতে এখনই খেলা শুরু করুন।"
                self.send_message(db, messenger_type, "resolve", text, user_id=u.id)
                count += 1

        # 7. Daily Winner Congrats
        elif scenario_type == MessageScenarioType.DAILY_WINNER_CONGRATS:
            # Scenario 7: External rank check.
            try:
                rank_data = requests.get("https://cms.quizard.live/money/weeklyWinnerByUserNData/").json()
                # Assuming JSON structure has a list of winners
                # Logic: Find winners with serial_no and link to our users by username/msisdn
                rank_data = [
                    {"msisdn": "1681791286", "points": 950, "rank": 1, "serial_no": 1},
                    {"msisdn": "1962401320", "points": 880, "rank": 2, "serial_no": 2},
                    {"msisdn": "1910194688", "points": 810, "rank": 3, "serial_no": 3},
                ]

                
                #make this loop enumerate from serial_no 1 to 50
                for item in rank_data:
                    serial_no = item.get("serial_no")

                    if serial_no > 50:
                        break

                    username = item.get("msisdn")
                    if username:
                        user = db.query(User).filter(User.username == username).first()
                        if user:
                            text = "অভিনন্দন! আজকের বিজয়ী তালিকায় থাকার জন্য আপনাকে আন্তরিক অভিনন্দন। পরবর্তী দিন গুলোর জন্য শুভকামনা। "
                            self.send_message(db, messenger_type, "resolve", text, user_id=user.id)
                            count += 1
            except:
                pass

        # 8. 12 PM Referral Promo
        elif scenario_type == MessageScenarioType.DAILY_REFERRAL_PROMO:
            # Scenario 8: Daily refer sms to all.
            all_users = db.query(User).all()
            for u in all_users:
                text = "আজই রেফার করে জিতে নিন পর পর তিন সপ্তাহে প্রাইজ জেতার সুযোগ!"
                self.send_message(db, messenger_type, "resolve", text, user_id=u.id)
                count += 1

        # 9. 3 Days Continuous Play
        elif scenario_type == MessageScenarioType.WEEKLY_WINNER_LIST_PROMO:
            # Scenario 9: 3 days continuous play.
            three_days_ago = date.today() - timedelta(days=2) # inclusive
            continuous = db.query(PlayedQuiz.user_id)\
                .filter(func.date(PlayedQuiz.created_at) >= three_days_ago)\
                .group_by(PlayedQuiz.user_id, func.date(PlayedQuiz.created_at))\
                .subquery()
            
            # Count distinct days in last 3 days per user
            streak_users = db.query(PlayedQuiz.user_id).filter(func.date(PlayedQuiz.created_at) >= three_days_ago)\
                .group_by(PlayedQuiz.user_id).having(func.count(func.distinct(func.date(PlayedQuiz.created_at))) >= 3).all()
            
            for u in streak_users:
                text = "আপনি সাপ্তাহিক উইনার হওয়ার তালিকায় রয়েছেন। অভিনন্দন! এভাবেই বেশি বেশি স্কোর করে যান। আপনার জন্য অপেক্ষা করছে সাপ্তাহিক পুরষ্কার !"
                self.send_message(db, messenger_type, "resolve", text, user_id=u.user_id)
                count += 1

        # 10. 10:30 Close-to-Winning Warning
        elif scenario_type == MessageScenarioType.WINNING_POSITION_WARNING:
            import json
            
            leaderboard_urls = {
                # Quizard
                "Ramadan Quiz Challenge": "https://cms.quizard.live/api/leaderboard/?portal=15&event_id=34",
                "Sports Quiz Arena": "https://cms.quizard.live/api/leaderboard/?portal=15&event_id=75",
                "Brain Power Quiz": "https://cms.quizard.live/api/leaderboard/?portal=15&event_id=149",
                "Eid Mega Tournament Quiz": "https://cms.quizard.live/api/leaderboard/?portal=15&event_id=150",
                # Wordly
                "Wordly English": "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=67",
                "Wordly Bangla": "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=79",
                "Spelling Bee": "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=134",
                "Memory Match": "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=151",
                "Sudoku Easy": "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=152",
                "Sudoku Medium": "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=153",
                "SudokuHard": "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=154",
                "Sudoku Expert": "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=155",
                # Arcaderush
                "Moto Race City": "https://arcaderush.xyz/Leaderboard/GetLeaderboard?gameName=Knife%20Madness&eventId=1001",
                "Knife Madness": "https://arcaderush.xyz/Leaderboard/GetLeaderboard?gameName=Knife%20Madness&eventId=1002",
                "20248 Crazy Merge": "https://arcaderush.xyz/Leaderboard/GetLeaderboard?gameName=Knife%20Madness&eventId=1003",
            }

            # Mock data 
            all_mock_data = {
                "https://cms.quizard.live/api/leaderboard/?portal=15&event_id=149": [
                     {"User_Rank": 55, "msisdn": "1962401320", "score": 57, "time_taken": 136, "round_number": 1, "date": "2026-01-12", "event_id": 149, "category": None, "win": 1, "name": "", "username": "1962401320", "avatar_id": None, "avatar_img": ""}
                ],
                "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=153": [
                    {"User_Rank": 1, "msisdn": "1628975383", "score": 59, "time_taken": 136, "round_number": 1, "date": "2026-01-07", "event_id": 153, "category": None, "win": 1, "name": "", "username": "1628975383", "avatar_id": None, "avatar_img": ""}
                ],
                "https://cms.quizard.live/api/leaderboard/?portal=18&event_id=151": [
                    {"User_Rank": 2, "msisdn": "1628975383", "score": 49, "time_taken": 156, "round_number": 1, "date": "2026-01-07", "event_id": 151, "category": None, "win": 1, "name": "Ullah", "username": "1628975383", "avatar_id": 1, "avatar_img": "images/20250417_180333.jpg"}
                ],
            }

            # Validating user helper (duplicated for safety)
            def get_user_by_msisdn(db: Session, msisdn: str) -> Optional[User]:
                # Try direct match first
                user = db.query(User).filter(User.username == msisdn).first()
                if user:
                    return user
                # Try with/without leading '0'
                if msisdn.startswith('0'):
                    user = db.query(User).filter(User.username == msisdn[1:]).first()
                else:
                    user = db.query(User).filter(User.username == '0' + msisdn).first()
                return user
            
            # This logic iterates ALL games in leaderboard_urls? 
            # Or should it only check for users who have subscriptions/activity?
            # Existing logic iterated all. We will iterate all urls to check rank.
            
            for game_name, url in leaderboard_urls.items():
                try:
                    # response = requests.get(url, timeout=15)
                    # response.raise_for_status()
                    # leaderboard_data = response.json()
                    
                    leaderboard_data = all_mock_data.get(url, [])

                    players = []
                    if "arcaderush.xyz" in url:
                        if isinstance(leaderboard_data, list):
                            for i, entry in enumerate(leaderboard_data):
                                if isinstance(entry, dict) and "username" in entry:
                                    players.append({"username": entry["username"], "rank": i + 1})
                    else: # Quizard/Wordly
                        if isinstance(leaderboard_data, list):
                            for entry in leaderboard_data:
                                if isinstance(entry, dict) and "msisdn" in entry and "User_Rank" in entry:
                                    players.append({"username": str(entry["msisdn"]), "rank": entry["User_Rank"]})
                    
                    for player in players:
                        rank = player["rank"]
                        # Warning if rank is not "good enough"? 
                        # User text: "আজকের ডেইলি প্রাইজ পাওয়া সম্ভব হবে না... রাত ১১.৫৯ এর মধ্যে “ “ তম অবস্থানের ভিতরে থাকলেই..."
                        # Currently hardcoded check > 50?
                        # Assuming threshold is 50 for now based on previous code.
                        TARGET_RANK = 50
                        
                        if rank > TARGET_RANK: # If rank is worse than 50
                            user = get_user_by_msisdn(db, player["username"])
                            if user:
                                text = f"ইতিমধ্যে জেনেছেন “ {game_name} “ গেমের লিডারবোর্ডে আপনার অবস্থান “ {rank} “ তম। এই অবস্থানে আজকের ডেইলি প্রাইজ পাওয়া সম্ভব হবে না। দয়া করে আরেকটু চেষ্টা করুন। রাত ১১.৫৯ এর মধ্যে “ {TARGET_RANK} “ তম অবস্থানের ভিতরে থাকলেই পেয়ে যাবেন ডেইলি প্রাইজ।"
                                self.send_message(db, messenger_type, "resolve", text, user_id=user.id)
                                count += 1

                except Exception as e:
                    logger.error(f"Failed to process leaderboard for WINNING_POSITION_WARNING from {url}: {e}")
                    continue

        return {"status": "success", "processed_count": count}

    def process_daily_check(self, db: Session, user_id: int) -> dict:
        """
        Check if user should receive a notification based on their game state.
        This logic simulates a business rule check.
        """
        # Circular import prevention if necessary, but ideally user_crud matches schemas
        from app.crud import user as user_crud
        
        user = user_crud.get(db, id=user_id)
        if not user:
            return {"status": "error", "message": "User not found"}
        
        # 1. Calculate current score (sum of all quiz scores for this user)
        # Note: Accessing relationship directly. If lazy loading issue, might need eager load in CRUD.
        current_score = sum([q.score for q in user.quizzes]) if user.quizzes else 0
        
        # 2. Define Winning Threshold
        WINNING_THRESHOLD = 50 
        
        # 3. Calculate Max Possible Remaining Score
        TOTAL_QUIZZES_ALLOWED = 5
        MAX_SCORE_PER_QUIZ = 10
        
        quizzes_taken = len(user.quizzes)
        quizzes_remaining = TOTAL_QUIZZES_ALLOWED - quizzes_taken
        
        if quizzes_remaining < 0:
            quizzes_remaining = 0
            
        max_possible_remaining_points = quizzes_remaining * MAX_SCORE_PER_QUIZ
        
        total_potential_score = current_score + max_possible_remaining_points
        
        if total_potential_score < WINNING_THRESHOLD:
            logger.info(f"User {user.username} cannot win (Potential: {total_potential_score} < Threshold: {WINNING_THRESHOLD}). Skipping notification.")
            return {"status": "skipped", "reason": "Impossible to win"}
            
        # 4. If possible to win, send notification
        # Check user's preferred messenger
        messenger_type = MessengerType.MAIL # Default
        receiver = user.email

        # Logic to pick best messenger
        # Priority: Telegram > WhatsApp > Discord > Email (Custom logic assumption)
        # Check if user has connected services
        has_telegram = False
        has_whatsapp = False
        has_discord = False
        
        if user.messenger:
            if user.messenger.telegram and user.messenger.telegram.get("chat_id"):
                has_telegram = True
            if user.messenger.whatsapp and user.messenger.whatsapp.get("phone"):
                has_whatsapp = True
            if user.messenger.discord and (user.messenger.discord.get("dm_channel_id") or user.messenger.discord.get("user_id")):
                has_discord = True
        
        if has_telegram:
            messenger_type = MessengerType.TELEGRAM
            receiver = str(user.messenger.telegram.get("chat_id")) # derived in send_message anyway, but good to be explicit
        elif has_whatsapp:
            messenger_type = MessengerType.WHATSAPP
            receiver = user.messenger.whatsapp.get("phone")
        elif user.phone_number: # Fallback to user phone if no explicit whatsapp profile but phone exists
            messenger_type = MessengerType.WHATSAPP
            receiver = user.phone_number
        elif has_discord:
            messenger_type = MessengerType.DISCORD
            receiver = "lookup_in_service" # send_message will resolve this if user_id is passed
            
        message_text = f"You are doing great! You have {current_score} points. You need {WINNING_THRESHOLD - current_score} more to win!"
        
        sent = self.send_message(db, messenger_type, receiver, message_text, user_id=user.id)
        
        if sent:
             return {"status": "success", "message": "Notification sent"}
        else:
             return {"status": "error", "message": "Failed to send notification"}

messaging_service = MessagingService()
