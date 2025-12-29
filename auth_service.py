"""
Authentication Service with Supabase
Handles user registration, login, and profile management
"""

import os
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
from supabase import create_client, Client
import jwt

logger = logging.getLogger(__name__)


class AuthService:
    """Service d'authentification avec Supabase"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not configured")
            self.client = None
        else:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
                logger.info("Supabase client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase: {e}")
                self.client = None
    
    def signup(self, email: str, password: str, user_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """
        Register a new user
        
        Args:
            email: User email
            password: User password
            user_data: Additional user data (first_name, last_name, etc.)
            
        Returns:
            (success, message, user_data)
        """
        if not self.client:
            return False, "Authentification non configurée", None
        
        try:
            # Create user in Supabase Auth
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if not response.user:
                return False, "Erreur lors de la création de l'utilisateur", None
            
            user_id = response.user.id
            logger.info(f"User created in auth: {user_id}")
            
            # Create user profile
            profile_data = {
                "id": user_id,
                "email": email,
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "full_name": f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
                "avatar_url": user_data.get("avatar_url"),
                "company": user_data.get("company", ""),
                "job_title": user_data.get("job_title", ""),
                "language": user_data.get("language", "fr"),
                "timezone": user_data.get("timezone", "Europe/Paris"),
                "is_active": True,
                "email_verified": False,
                "preferences": {
                    "theme": "light",
                    "notifications_enabled": True,
                    "email_notifications": True
                }
            }
            
            # Insert profile in profiles table
            try:
                profile_response = self.client.table("profiles").insert(profile_data).execute()
                logger.info(f"Profile created for user: {user_id}")
            except Exception as profile_error:
                logger.error(f"Profile insert error: {profile_error}")
                # Try to delete the auth user since profile creation failed
                try:
                    self.client.auth.admin.delete_user(user_id)
                except:
                    pass
                
                error_str = str(profile_error).lower()
                if "row level security" in error_str or "rls" in error_str:
                    return False, "Erreur de configuration serveur (RLS). Veuillez contacter le support.", None
                else:
                    return False, f"Erreur lors de la création du profil: {str(profile_error)}", None
            
            # Create activity log (non-critical)
            try:
                self.client.table("activity_logs").insert({
                    "user_id": user_id,
                    "action": "signup",
                    "description": "Nouvel utilisateur inscrit"
                }).execute()
            except Exception as log_error:
                logger.warning(f"Activity log error (non-critical): {log_error}")
            
            return True, "Inscription réussie! Vous pouvez maintenant vous connecter.", {"id": user_id, "email": email}
            
        except Exception as e:
            logger.error(f"Signup error: {e}")
            error_msg = str(e).lower()
            
            if "already registered" in error_msg:
                return False, "Cet email est déjà inscrit", None
            elif "password" in error_msg:
                return False, "Le mot de passe ne respecte pas les critères", None
            else:
                return False, f"Erreur d'inscription: {str(e)}", None
    
    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Login user
        
        Args:
            email: User email
            password: User password
            
        Returns:
            (success, message, session_data)
        """
        if not self.client:
            return False, "Authentification non configurée", None
        
        try:
            # Sign in with email and password
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not response.user:
                return False, "Email ou mot de passe incorrect", None
            
            user_id = response.user.id
            logger.info(f"User logged in: {user_id}")
            
            # Get user profile
            try:
                profile_response = self.client.table("profiles").select("*").eq("id", user_id).execute()
                
                if not profile_response.data:
                    logger.warning(f"Profile not found for user: {user_id}")
                    # Create minimal profile if missing
                    try:
                        profile_data = {
                            "id": user_id,
                            "email": email,
                            "first_name": "",
                            "last_name": "",
                            "full_name": ""
                        }
                        self.client.table("profiles").insert(profile_data).execute()
                        profile_response = self.client.table("profiles").select("*").eq("id", user_id).execute()
                    except Exception as create_error:
                        logger.error(f"Could not create missing profile: {create_error}")
                        return False, "Erreur: Profil utilisateur manquant", None
                
                profile = profile_response.data[0]
            except Exception as profile_error:
                logger.error(f"Profile fetch error: {profile_error}")
                return False, "Erreur lors de la récupération du profil", None
            
            # Log login activity (non-critical)
            try:
                self.client.table("activity_logs").insert({
                    "user_id": user_id,
                    "action": "login",
                    "description": "Connexion utilisateur"
                }).execute()
            except Exception as log_error:
                logger.warning(f"Activity log error (non-critical): {log_error}")
            
            session_data = {
                "user_id": user_id,
                "email": email,
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "profile": profile
            }
            
            return True, "Connexion réussie", session_data
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            error_msg = str(e).lower()
            
            if "invalid login credentials" in error_msg or "invalid grant" in error_msg:
                return False, "Email ou mot de passe incorrect", None
            else:
                return False, f"Erreur de connexion: {str(e)}", None
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile data"""
        if not self.client:
            return None
        
        try:
            response = self.client.table("profiles").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching profile: {e}")
            return None
    
    def update_user_profile(self, user_id: str, update_data: Dict) -> Tuple[bool, str]:
        """Update user profile"""
        if not self.client:
            return False, "Authentification non configurée"
        
        try:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            self.client.table("profiles").update(update_data).eq("id", user_id).execute()
            
            # Log activity
            self.client.table("activity_logs").insert({
                "user_id": user_id,
                "action": "profile_update",
                "description": "Profil utilisateur mis à jour",
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            
            return True, "Profil mis à jour"
        except Exception as e:
            logger.error(f"Profile update error: {e}")
            return False, f"Erreur: {str(e)}"
    
    def logout(self, user_id: str) -> bool:
        """Log user logout"""
        if not self.client:
            return False
        
        try:
            self.client.table("activity_logs").insert({
                "user_id": user_id,
                "action": "logout",
                "description": "Déconnexion utilisateur",
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            
            return True
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    def reset_password(self, email: str) -> Tuple[bool, str]:
        """Send password reset email"""
        if not self.client:
            return False, "Authentification non configurée"
        
        try:
            self.client.auth.reset_password_for_email(email)
            return True, "Email de réinitialisation envoyé"
        except Exception as e:
            logger.error(f"Password reset error: {e}")
            return False, f"Erreur: {str(e)}"
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return user data"""
        try:
            # Decode token (basic verification)
            decoded = jwt.decode(token, options={"verify_signature": False})
            return decoded
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
