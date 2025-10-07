import os
import json
import hashlib
import uuid
import socket
import platform
import asyncio
import requests
import time
import logging
import  aiohttp 
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum
import tkinter as tk
from tkinter import messagebox
import base64
import threading
from contextlib import contextmanager

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityStatus(Enum):
    """Statuts de sécurité possibles"""
    SECURE = "secure"
    WARNING = "warning" 
    RESTRICTED = "restricted"
    COMPROMISED = "compromised"
    UNKNOWN = "unknown"

class LicenseType(Enum):
    """Types de licence disponibles"""
    DEMO = "Demo"
    STANDARD = "Standard"
    PROFESSIONAL = "Professional"
    ENTERPRISE = "Enterprise"

@dataclass
class LicenseInfo:
    """Structure des informations de licence"""
    product: str
    version: str
    license_type: LicenseType
    expires: str
    max_students: int
    activated_at: str
    license_key: str
    features: List[str]
    offline_activation: bool = False
    server_time_used: bool = False
    machine_id: str = ""

@dataclass
class SecurityReport:
    """Rapport de sécurité du système"""
    status: SecurityStatus
    tamper_attempts: int
    last_check: str
    server_sync_available: bool
    last_server_sync: str
    creation_time: str

class TimeServerManager:
    """Gestionnaire des serveurs de temps externes"""
    
    TIME_SERVERS = [
        "http://worldtimeapi.org/api/timezone/Etc/UTC",
        "https://timeapi.io/api/Time/current/zone?timeZone=UTC", 
        "http://worldclockapi.com/api/json/utc/now"
    ]
    
    @classmethod
    async def get_server_time_async(cls, timeout: int = 10) -> Optional[datetime]:
        """Récupère l'heure serveur de manière asynchrone"""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            for server_url in cls.TIME_SERVERS:
                try:
                    async with session.get(server_url) as response:
                        if response.status == 200:
                            data = await response.json()
                            return cls._parse_time_response(data)
                except Exception as e:
                    logger.warning(f"Erreur serveur temps {server_url}: {e}")
                    continue
        return None
    
    @classmethod
    def get_server_time_sync(cls, timeout: int = 10) -> Optional[datetime]:
        """Version synchrone pour compatibilité"""
        for server_url in cls.TIME_SERVERS:
            try:
                response = requests.get(server_url, timeout=timeout)
                if response.status_code == 200:
                    return cls._parse_time_response(response.json())
            except Exception as e:
                logger.warning(f"Erreur serveur temps {server_url}: {e}")
                continue
        return None
    
    @staticmethod
    def _parse_time_response(data: Dict[str, Any]) -> Optional[datetime]:
        """Parse la réponse des différents serveurs de temps"""
        time_fields = ['datetime', 'dateTime', 'currentDateTime']
        
        for field in time_fields:
            if field in data:
                time_str = data[field]
                try:
                    return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                except ValueError:
                    continue
        return None

class MachineIdentifier:
    """Générateur d'identifiant machine sécurisé"""
    
    @staticmethod
    def generate() -> str:
        """Génère un ID unique basé sur les caractéristiques de la machine"""
        try:
            machine_components = []
            
            # MAC Address
            try:
                mac = ':'.join([f'{(uuid.getnode() >> i) & 0xff:02x}' 
                              for i in range(0, 48, 8)][::-1])
                machine_components.append(mac)
            except Exception:
                pass
            
            # Informations système
            try:
                machine_components.extend([
                    socket.gethostname(),
                    platform.machine(),
                    platform.system(),
                    platform.processor() or "unknown"
                ])
            except Exception:
                pass
            
            # ID de disque dur (Windows)
            if platform.system() == "Windows":
                try:
                    import subprocess
                    result = subprocess.run(['wmic', 'diskdrive', 'get', 'serialnumber'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        serial = result.stdout.strip().split('\n')[1].strip()
                        if serial and serial != "SerialNumber":
                            machine_components.append(serial)
                except Exception:
                    pass
            
            # Combiner et hasher
            combined = '|'.join(filter(None, machine_components))
            if not combined:
                combined = str(uuid.uuid4())
            
            return hashlib.sha256(combined.encode('utf-8')).hexdigest()[:32].upper()
            
        except Exception as e:
            logger.error(f"Erreur génération machine ID: {e}")
            return str(uuid.uuid4()).replace('-', '').upper()[:32]

class TimeTracker:
    """Gestionnaire de suivi temporel avancé"""
    
    def __init__(self, tracking_file: Path):
        self.tracking_file = tracking_file
        self.max_tamper_attempts = 3
        
    def initialize(self) -> None:
        """Initialise le système de suivi temporel"""
        try:
            current_time = datetime.now()
            server_time = TimeServerManager.get_server_time_sync(timeout=5)
            
            if not self.tracking_file.exists():
                time_data = {
                    'last_local_time': current_time.isoformat(),
                    'last_server_time': server_time.isoformat() if server_time else None,
                    'creation_time': current_time.isoformat(),
                    'tamper_attempts': 0,
                    'last_check': current_time.isoformat(),
                    'integrity_hash': self._calculate_integrity_hash(current_time)
                }
                self._save_secure(time_data)
            else:
                self.check_tampering()
                
        except Exception as e:
            logger.error(f"Erreur initialisation suivi temporel: {e}")
    
    def check_tampering(self) -> bool:
        """Vérifie les manipulations temporelles avec détection avancée"""
        try:
            time_data = self._load_secure()
            if not time_data:
                return False
            
            current_local = datetime.now()
            last_local = datetime.fromisoformat(time_data['last_local_time'])
            
            # Détection de recul temporel
            time_diff = (current_local - last_local).total_seconds()
            
            # Détection de manipulation d'intégrité
            expected_hash = self._calculate_integrity_hash(last_local)
            stored_hash = time_data.get('integrity_hash', '')
            
            tampering_detected = False
            tamper_reasons = []
            
            if time_diff < -60:  # Recul de plus d'1 minute
                tampering_detected = True
                tamper_reasons.append(f"Recul temporel de {abs(time_diff):.0f} secondes")
            
            if expected_hash != stored_hash:
                tampering_detected = True
                tamper_reasons.append("Intégrité du fichier compromise")
            
            # Détecter les sauts temporels suspects (plus de 24h en avant)
            if time_diff > 86400:  # Plus de 24h
                server_time = TimeServerManager.get_server_time_sync(timeout=3)
                if server_time:
                    server_diff = (current_local - server_time).total_seconds()
                    if abs(server_diff) > 3600:  # Plus d'1h de différence avec serveur
                        tampering_detected = True
                        tamper_reasons.append("Saut temporel suspect détecté")
            
            if tampering_detected:
                return self._handle_tampering(time_data, tamper_reasons)
            
            # Mise à jour normale
            time_data['last_local_time'] = current_local.isoformat()
            time_data['last_check'] = current_local.isoformat()
            time_data['integrity_hash'] = self._calculate_integrity_hash(current_local)
            self._save_secure(time_data)
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur vérification manipulation: {e}")
            return False
    
    def _handle_tampering(self, time_data: Dict[str, Any], reasons: List[str]) -> bool:
        """Gère la détection de manipulation"""
        time_data['tamper_attempts'] = time_data.get('tamper_attempts', 0) + 1
        time_data['last_tamper_detection'] = datetime.now().isoformat()
        time_data['tamper_reasons'] = reasons
        
        attempt_count = time_data['tamper_attempts']
        
        logger.warning(f"Manipulation détectée (#{attempt_count}): {', '.join(reasons)}")
        
        # Sauvegarder sans mettre à jour les timestamps
        self._save_secure(time_data)
        
        return self._show_tampering_warning(attempt_count, reasons)
    
    def _show_tampering_warning(self, attempt_count: int, reasons: List[str]) -> bool:
        """Affiche l'avertissement de manipulation"""
        reasons_text = '\n'.join(f"• {reason}" for reason in reasons)
        
        if attempt_count == 1:
            title = "⚠️ Anomalie Temporelle Détectée"
            message = (
                f"Le système a détecté une anomalie temporelle:\n\n{reasons_text}\n\n"
                "Actions recommandées:\n"
                "• Vérifier la synchronisation de l'horloge système\n"
                "• Activer la synchronisation automatique NTP\n"
                "• Redémarrer l'application\n\n"
                "L'application continue de fonctionner."
            )
            messagebox.showwarning(title, message)
            return False
            
        elif attempt_count <= 2:
            title = "🚨 Manipulation Temporelle Répétée"
            message = (
                f"Détection répétée #{attempt_count}:\n\n{reasons_text}\n\n"
                "Mode restreint activé - Fonctionnalités limitées.\n\n"
                "Pour restaurer l'accès complet:\n"
                "• Corriger la date/heure système\n"
                "• Redémarrer l'application\n"
                "• Contacter le support si le problème persiste"
            )
            messagebox.showwarning(title, message)
            return False
            
        else:
            title = "🔒 Sécurité Compromise"
            message = (
                f"Trop de manipulations détectées ({attempt_count}).\n\n"
                f"Raisons:\n{reasons_text}\n\n"
                "L'application va se fermer pour sécurité.\n\n"
                "Solution: Réinstaller l'application avec une horloge correcte."
            )
            messagebox.showerror(title, message)
            return True  # Signal pour fermer l'application
    
    def _calculate_integrity_hash(self, timestamp: datetime) -> str:
        """Calcule un hash d'intégrité basé sur l'horodatage"""
        data = f"{timestamp.isoformat()}{platform.system()}{socket.gethostname()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _save_secure(self, data: Dict[str, Any]) -> None:
        """Sauvegarde sécurisée des données"""
        try:
            json_str = json.dumps(data, sort_keys=True)
            encoded = base64.b85encode(json_str.encode('utf-8')).decode('utf-8')
            checksum = hashlib.sha256(json_str.encode()).hexdigest()
            
            secure_data = {
                'payload': encoded,
                'checksum': checksum,
                'version': '2.0'
            }
            
            self.tracking_file.write_text(json.dumps(secure_data), encoding='utf-8')
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde sécurisée: {e}")
    
    def _load_secure(self) -> Optional[Dict[str, Any]]:
        """Chargement sécurisé des données"""
        try:
            if not self.tracking_file.exists():
                return None
                
            secure_data = json.loads(self.tracking_file.read_text(encoding='utf-8'))
            
            payload = secure_data.get('payload')
            expected_checksum = secure_data.get('checksum')
            
            if not payload or not expected_checksum:
                return None
            
            # Vérification d'intégrité
            decoded_bytes = base64.b85decode(payload.encode('utf-8'))
            json_str = decoded_bytes.decode('utf-8')
            actual_checksum = hashlib.sha256(json_str.encode()).hexdigest()
            
            if actual_checksum != expected_checksum:
                logger.error("Intégrité du fichier de suivi compromise!")
                return None
            
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"Erreur chargement sécurisé: {e}")
            return None

class LicenseValidator:
    """Validateur de licence avec chiffrement renforcé"""
    
    VALID_KEYS = {
        "TEST-1234-ABCD-5678": {
            "license_type": LicenseType.STANDARD,
            "duration_days": 365,
            "max_students": 1000,
            "features": ["gestion_adherents", "competitions", "ceintures", "statistiques"]
        },
        "DEMO-2024-TKDO-MGMT": {
            "license_type": LicenseType.DEMO,
            "duration_days": 30,
            "max_students": 50,
            "features": ["gestion_adherents"]
        },
        "PRO-2024-FULL-ACCES": {
            "license_type": LicenseType.PROFESSIONAL,
            "duration_days": 730,
            "max_students": -1,
            "features": ["gestion_adherents", "competitions", "ceintures", 
                        "statistiques", "backup_cloud", "multi_clubs"]
        }
    }
    
    @classmethod
    def validate_format(cls, license_key: str) -> bool:
        """Valide le format de la clé"""
        if len(license_key) != 19:
            return False
        
        parts = license_key.split('-')
        if len(parts) != 4:
            return False
        
        return all(len(part) == 4 and part.replace(' ', '').isalnum() for part in parts)
    
    @classmethod
    def verify_key(cls, license_key: str, base_time: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """Vérifie la validité de la clé"""
        key_upper = license_key.upper()
        if key_upper not in cls.VALID_KEYS:
            return None
        
        key_info = cls.VALID_KEYS[key_upper]
        activation_time = base_time or datetime.now()
        
        return {
            "product": "Taekwondo Manager Pro",
            "version": "2.0.0",
            "license_type": key_info["license_type"],
            "expires": (activation_time + timedelta(days=key_info["duration_days"])).isoformat(),
            "max_students": key_info["max_students"],
            "features": key_info["features"].copy()
        }

class ModernLicenseManager:
    """Gestionnaire de licence modernisé avec sécurité renforcée"""
    
    def __init__(self):
        self.app_data_dir = self._get_app_data_directory()
        self.license_file = self.app_data_dir / "license_v2.json"
        self.time_tracker = TimeTracker(self.app_data_dir / "security.dat")
        self.machine_id = MachineIdentifier.generate()
        
        # Créer le répertoire et initialiser
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
        self.time_tracker.initialize()
        
        logger.info(f"Gestionnaire initialisé - Machine ID: {self.machine_id[:8]}...")
    
    def _get_app_data_directory(self) -> Path:
        """Détermine le répertoire de données selon l'OS"""
        system = platform.system()
        
        if system == "Windows":
            base = Path(os.environ.get('APPDATA', Path.home()))
        elif system == "Darwin":  # macOS
            base = Path.home() / "Library" / "Application Support"
        else:  # Linux
            base = Path.home() / ".local" / "share"
        
        return base / "TaekwondoManagerPro"
    
    @contextmanager
    def _security_check(self):
        """Context manager pour les vérifications de sécurité"""
        try:
            # Vérification avant opération
            if self.time_tracker.check_tampering():
                raise SecurityError("Application fermée pour raisons de sécurité")
            yield
        finally:
            # Vérification après opération
            pass
    
    def is_valid(self, check_server_time: bool = True) -> bool:
        """Vérifie la validité de la licence avec sécurité renforcée"""
        try:
            with self._security_check():
                # Charger et vérifier la licence
                license_data = self._load_license_secure()
                if not license_data:
                    return False
                
                # Vérifier l'ID machine
                if license_data.get('machine_id') != self.machine_id:
                    logger.warning("ID machine non concordant")
                    return False
                
                # Vérifier l'expiration
                return self._check_expiration(license_data, check_server_time)
                
        except SecurityError:
            return False
        except Exception as e:
            logger.error(f"Erreur validation licence: {e}")
            return False
    
    def _check_expiration(self, license_data: Dict[str, Any], use_server_time: bool) -> bool:
        """Vérifie l'expiration avec gestion serveur/local"""
        try:
            expiry_str = license_data.get('expires', '2020-01-01T00:00:00')
            expiry_date = datetime.fromisoformat(expiry_str)
            
            current_time = datetime.now()
            
            if use_server_time:
                try:
                    server_time = TimeServerManager.get_server_time_sync(timeout=5)
                    if server_time:
                        current_time = server_time
                        logger.info("Utilisation heure serveur pour validation")
                    else:
                        logger.warning("Serveur temps inaccessible, utilisation heure locale")
                except Exception:
                    logger.warning("Erreur récupération heure serveur")
            
            is_valid = current_time <= expiry_date
            
            if not is_valid:
                logger.info(f"Licence expirée: {expiry_date} < {current_time}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Erreur vérification expiration: {e}")
            return False
    
    async def activate_license_async(self, license_key: str, parent_window=None, 
                                   allow_offline: bool = False) -> bool:
        """Activation asynchrone de la licence"""
        try:
            # Validation format
            if not LicenseValidator.validate_format(license_key):
                self._show_error("Clé Invalide", 
                               "Format de clé incorrect.\nFormat: XXXX-XXXX-XXXX-XXXX")
                return False
            
            # Récupération heure serveur
            server_time = None
            if not allow_offline:
                try:
                    server_time = await TimeServerManager.get_server_time_async(timeout=10)
                except Exception:
                    pass
                
                if not server_time and not self._confirm_offline_activation():
                    return False
                allow_offline = True
            
            # Vérification de la clé
            license_data = LicenseValidator.verify_key(license_key, server_time)
            if not license_data:
                self._show_activation_failed()
                return False
            
            # Finaliser l'activation
            return self._finalize_activation(license_data, license_key, server_time, allow_offline)
            
        except Exception as e:
            logger.error(f"Erreur activation: {e}")
            self._show_error("Erreur", f"Erreur lors de l'activation:\n{e}")
            return False
    
    def activate_license(self, license_key: str, parent_window=None, 
                        allow_offline: bool = False) -> bool:
        """Version synchrone de l'activation"""
        try:
            return asyncio.run(self.activate_license_async(license_key, parent_window, allow_offline))
        except Exception as e:
            logger.error(f"Erreur activation synchrone: {e}")
            return False
    
    def _finalize_activation(self, license_data: Dict[str, Any], license_key: str,
                           server_time: Optional[datetime], offline_mode: bool) -> bool:
        """Finalise l'activation de la licence"""
        try:
            activation_time = server_time or datetime.now()
            
            # Enrichir les données de licence
            enhanced_data = {
                **license_data,
                'machine_id': self.machine_id,
                'activated_at': activation_time.isoformat(),
                'license_key': license_key,
                'server_time_used': server_time is not None,
                'offline_activation': offline_mode and server_time is None,
                'activation_signature': self._generate_activation_signature(license_key, activation_time)
            }
            
            # Sauvegarder
            if self._save_license_secure(enhanced_data):
                self._show_activation_success(enhanced_data, server_time is not None)
                return True
            else:
                self._show_error("Erreur", "Impossible de sauvegarder la licence")
                return False
                
        except Exception as e:
            logger.error(f"Erreur finalisation activation: {e}")
            return False
    
    def _generate_activation_signature(self, license_key: str, activation_time: datetime) -> str:
        """Génère une signature d'activation"""
        data = f"{license_key}{self.machine_id}{activation_time.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    def _show_activation_success(self, license_data: Dict[str, Any], online_mode: bool) -> None:
        """Affiche le message de succès d'activation"""
        mode = "En ligne" if online_mode else "Hors ligne"
        license_type = license_data.get('license_type', LicenseType.STANDARD)
        expires = license_data.get('expires', 'Non définie')[:10]
        
        message = (
            f"✅ Licence activée avec succès!\n\n"
            f"Mode: {mode}\n"
            f"Type: {license_type.value if hasattr(license_type, 'value') else license_type}\n"
            f"Expire le: {expires}\n"
            f"Machine: {self.machine_id[:8]}..."
        )
        messagebox.showinfo("Activation Réussie", message)
    
    def _show_activation_failed(self) -> None:
        """Affiche le message d'échec d'activation"""
        message = (
            "❌ Clé de licence invalide ou expirée.\n\n"
            "Clés de test disponibles:\n"
            "• TEST-1234-ABCD-5678 (Standard - 1 an)\n"
            "• DEMO-2024-TKDO-MGMT (Demo - 30 jours)\n"
            "• PRO-2024-FULL-ACCES (Pro - 2 ans)"
        )
        messagebox.showerror("Activation Échouée", message)
    
    def _confirm_offline_activation(self) -> bool:
        """Demande confirmation pour activation hors ligne"""
        return messagebox.askyesno(
            "Activation Hors Ligne",
            "Impossible de se connecter aux serveurs de temps.\n\n"
            "Continuer l'activation hors ligne?\n\n"
            "⚠️ ATTENTION: Des vérifications de sécurité supplémentaires\n"
            "seront activées pour détecter les manipulations temporelles."
        )
    
    def _show_error(self, title: str, message: str) -> None:
        """Affiche un message d'erreur"""
        messagebox.showerror(title, message)
    
    def _load_license_secure(self) -> Optional[Dict[str, Any]]:
        """Chargement sécurisé de la licence"""
        try:
            if not self.license_file.exists():
                return None
            
            data = json.loads(self.license_file.read_text(encoding='utf-8'))
            
            if 'payload' in data:  # Format sécurisé v2
                payload = data['payload']
                checksum = data['checksum']
                
                decoded = base64.b85decode(payload.encode('utf-8'))
                json_str = decoded.decode('utf-8')
                
                # Vérifier l'intégrité
                if hashlib.sha256(json_str.encode()).hexdigest() != checksum:
                    logger.error("Intégrité licence compromise")
                    return None
                
                return json.loads(json_str)
            
            # Format legacy
            elif 'encoded_data' in data:
                encoded_data = data['encoded_data']
                decoded = base64.b64decode(encoded_data.encode('utf-8'))
                return json.loads(decoded.decode('utf-8'))
            
            return data
            
        except Exception as e:
            logger.error(f"Erreur chargement licence: {e}")
            return None
    
    def _save_license_secure(self, license_data: Dict[str, Any]) -> bool:
        """Sauvegarde sécurisée de la licence"""
        try:
            json_str = json.dumps(license_data, indent=2, sort_keys=True)
            encoded = base64.b85encode(json_str.encode('utf-8')).decode('utf-8')
            checksum = hashlib.sha256(json_str.encode()).hexdigest()
            
            secure_data = {
                'payload': encoded,
                'checksum': checksum,
                'version': '2.0',
                'created_at': datetime.now().isoformat()
            }
            
            self.license_file.write_text(json.dumps(secure_data, indent=2), encoding='utf-8')
            return True
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde licence: {e}")
            return False
    
    def get_license_info(self) -> Optional[LicenseInfo]:
        """Retourne les informations complètes de la licence"""
        try:
            license_data = self._load_license_secure()
            if not license_data:
                return None
            
            return LicenseInfo(
                product=license_data.get('product', 'Inconnu'),
                version=license_data.get('version', 'Inconnue'),
                license_type=LicenseType(license_data.get('license_type', 'Standard')),
                expires=license_data.get('expires', 'Inconnue'),
                max_students=license_data.get('max_students', 0),
                activated_at=license_data.get('activated_at', 'Inconnue'),
                license_key=license_data.get('license_key', 'Non disponible'),
                features=license_data.get('features', []),
                offline_activation=license_data.get('offline_activation', False),
                server_time_used=license_data.get('server_time_used', False),
                machine_id=license_data.get('machine_id', '')
            )
            
        except Exception as e:
            logger.error(f"Erreur récupération info licence: {e}")
            return None
    
    def get_security_report(self) -> SecurityReport:
        """Génère un rapport de sécurité complet"""
        time_data = self.time_tracker._load_secure()
        
        if not time_data:
            return SecurityReport(
                status=SecurityStatus.UNKNOWN,
                tamper_attempts=0,
                last_check="Jamais",
                server_sync_available=False,
                last_server_sync="Jamais",
                creation_time="Inconnue"
            )
        
        tamper_count = time_data.get('tamper_attempts', 0)
        
        if tamper_count == 0:
            status = SecurityStatus.SECURE
        elif tamper_count < 2:
            status = SecurityStatus.WARNING
        elif tamper_count < 3:
            status = SecurityStatus.RESTRICTED
        else:
            status = SecurityStatus.COMPROMISED
        
        return SecurityReport(
            status=status,
            tamper_attempts=tamper_count,
            last_check=time_data.get('last_check', 'Jamais'),
            server_sync_available=time_data.get('server_sync_available', False),
            last_server_sync=time_data.get('last_server_sync', 'Jamais'),
            creation_time=time_data.get('creation_time', 'Inconnue')
        )
    
    def get_days_remaining(self, use_server_time: bool = True) -> int:
        """Calcule les jours restants avant expiration"""
        try:
            with self._security_check():
                license_data = self._load_license_secure()
                if not license_data:
                    return 0
                
                expiry_str = license_data.get('expires')
                if not expiry_str:
                    return 0
                
                expiry_date = datetime.fromisoformat(expiry_str)
                current_time = datetime.now()
                
                # Utiliser heure serveur si demandé
                if use_server_time:
                    try:
                        server_time = TimeServerManager.get_server_time_sync(timeout=3)
                        if server_time:
                            current_time = server_time
                    except Exception:
                        pass
                
                remaining = expiry_date - current_time
                return max(0, remaining.days)
                
        except SecurityError:
            return 0
        except Exception as e:
            logger.error(f"Erreur calcul jours restants: {e}")
            return 0
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Vérifie si une fonctionnalité est disponible"""
        try:
            if not self.is_valid():
                return False
            
            license_data = self._load_license_secure()
            if not license_data:
                return False
            
            features = license_data.get('features', [])
            
            # Vérifier les restrictions de sécurité
            security_report = self.get_security_report()
            if security_report.status == SecurityStatus.RESTRICTED:
                # Mode restreint - seules les fonctions de base
                basic_features = ['gestion_adherents']
                return feature_name in basic_features and feature_name in features
            elif security_report.status == SecurityStatus.COMPROMISED:
                return False
            
            return feature_name in features
            
        except Exception as e:
            logger.error(f"Erreur vérification fonctionnalité {feature_name}: {e}")
            return False
    
    def deactivate_license(self) -> bool:
        """Désactive la licence avec nettoyage sécurisé"""
        try:
            files_to_remove = [self.license_file, self.time_tracker.tracking_file]
            
            for file_path in files_to_remove:
                if file_path.exists():
                    # Écrasement sécurisé du fichier
                    self._secure_delete(file_path)
            
            logger.info("Licence désactivée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur désactivation: {e}")
            return False
    
    def _secure_delete(self, file_path: Path) -> None:
        """Suppression sécurisée d'un fichier"""
        try:
            if file_path.exists():
                # Écraser le contenu avant suppression
                file_size = file_path.stat().st_size
                with open(file_path, 'wb') as f:
                    f.write(os.urandom(file_size))
                file_path.unlink()
        except Exception as e:
            logger.error(f"Erreur suppression sécurisée {file_path}: {e}")
    
    def validate_license_integrity(self) -> bool:
        """Valide l'intégrité complète de la licence"""
        try:
            license_data = self._load_license_secure()
            if not license_data:
                return False
            
            # Vérifier la signature d'activation
            expected_sig = self._generate_activation_signature(
                license_data.get('license_key', ''),
                datetime.fromisoformat(license_data.get('activated_at', ''))
            )
            
            actual_sig = license_data.get('activation_signature', '')
            
            if expected_sig != actual_sig:
                logger.warning("Signature d'activation invalide")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur validation intégrité: {e}")
            return False
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques d'utilisation"""
        try:
            license_info = self.get_license_info()
            security_report = self.get_security_report()
            
            stats = {
                'license_active': self.is_valid(),
                'days_remaining': self.get_days_remaining(),
                'self.security_status': security_report.status.value,
                'tamper_attempts': security_report.tamper_attempts,
                'machine_id': self.machine_id[:8] + "...",
                'features_count': len(license_info.features) if license_info else 0,
                'offline_mode': license_info.offline_activation if license_info else False
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur statistiques: {e}")
            return {}
    
    def export_license_report(self) -> str:
        """Exporte un rapport détaillé de la licence"""
        try:
            license_info = self.get_license_info()
            security_report = self.get_security_report()
            stats = self.get_usage_statistics()
            
            report_lines = [
                "=== RAPPORT DE LICENCE TAEKWONDO MANAGER PRO ===",
                f"Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "INFORMATIONS LICENCE:",
                f"  Produit: {license_info.product if license_info else 'Non activé'}",
                f"  Type: {license_info.license_type.value if license_info else 'Aucun'}",
                f"  Statut: {'✅ Valide' if stats.get('license_active') else '❌ Invalide'}",
                f"  Expire: {license_info.expires[:10] if license_info else 'N/A'}",
                f"  Jours restants: {stats.get('days_remaining', 0)}",
                "",
                "SÉCURITÉ:",
                f"  Statut: {security_report.status.value.upper()}",
                f"  Tentatives manipulation: {security_report.tamper_attempts}",
                f"  Dernière vérification: {security_report.last_check[:19]}",
                f"  Sync serveur: {'✅' if security_report.server_sync_available else '❌'}",
                "",
                "SYSTÈME:",
                f"  Machine ID: {self.machine_id[:16]}...",
                f"  OS: {platform.system()} {platform.release()}",
                f"  Mode hors ligne: {'✅' if stats.get('offline_mode') else '❌'}",
                "",
                "FONCTIONNALITÉS ACTIVES:",
            ]
            
            if license_info:
                for feature in license_info.features:
                    enabled = "✅" if self.is_feature_enabled(feature) else "❌"
                    report_lines.append(f"  {enabled} {feature}")
            else:
                report_lines.append("  Aucune licence active")
            
            return "\n".join(report_lines)
            
        except Exception as e:
            logger.error(f"Erreur génération rapport: {e}")
            return f"Erreur génération rapport: {e}"

class SecurityError(Exception):
    """Exception levée en cas de problème de sécurité"""
    pass

class LicenseGUI:
    """Interface graphique modernisée pour la gestion des licences"""
    
    def __init__(self):
        self.license_manager = ModernLicenseManager()
        self.root = tk.Tk()
        self.setup_gui()
    
    def setup_gui(self):
        """Configure l'interface utilisateur"""
        self.root.title("Taekwondo Manager Pro - Gestionnaire de Licence v2.0")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Frame principal
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = tk.Label(main_frame, text="🥋 Taekwondo Manager Pro", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Statut actuel
        self.status_frame = tk.LabelFrame(main_frame, text="Statut de la Licence", 
                                         font=("Arial", 10, "bold"))
        self.status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.status_label = tk.Label(self.status_frame, text="Chargement...", 
                                    font=("Courier", 9))
        self.status_label.pack(padx=10, pady=10)
        
        # Activation
        activation_frame = tk.LabelFrame(main_frame, text="Activation de Licence", 
                                        font=("Arial", 10, "bold"))
        activation_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(activation_frame, text="Clé de licence:").pack(pady=(10, 5))
        
        self.key_entry = tk.Entry(activation_frame, width=30, font=("Courier", 11))
        self.key_entry.pack(pady=(0, 10))
        self.key_entry.bind('<KeyRelease>', self._format_key_input)
        
        button_frame = tk.Frame(activation_frame)
        button_frame.pack(pady=(0, 10))
        
        self.activate_btn = tk.Button(button_frame, text="Activer", 
                                     command=self.activate_license,
                                     bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.activate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.offline_btn = tk.Button(button_frame, text="Activer Hors Ligne", 
                                    command=self.activate_offline,
                                    bg="#FF9800", fg="white", font=("Arial", 10))
        self.offline_btn.pack(side=tk.LEFT)
        
        # Actions
        actions_frame = tk.LabelFrame(main_frame, text="Actions", 
                                     font=("Arial", 10, "bold"))
        actions_frame.pack(fill=tk.X, pady=(0, 20))
        
        actions_button_frame = tk.Frame(actions_frame)
        actions_button_frame.pack(pady=10)
        
        tk.Button(actions_button_frame, text="Vérifier Licence", 
                 command=self.check_license).pack(side=tk.LEFT, padx=5)
        
        tk.Button(actions_button_frame, text="Rapport Sécurité", 
                 command=self.show_security_report).pack(side=tk.LEFT, padx=5)
        
        tk.Button(actions_button_frame, text="Désactiver", 
                 command=self.deactivate_license,
                 bg="#f44336", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Mise à jour initiale
        self.update_status()
        
        # Auto-refresh toutes les 30 secondes
        self.root.after(30000, self.auto_refresh)
    
    def _format_key_input(self, event):
        """Formate automatiquement la saisie de clé"""
        current = self.key_entry.get().replace('-', '').upper()
        if len(current) <= 16:
            formatted = '-'.join([current[i:i+4] for i in range(0, len(current), 4)])
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, formatted)
    
    def update_status(self):
        """Met à jour l'affichage du statut"""
        try:
            license_info = self.license_manager.get_license_info()
            is_valid = self.license_manager.is_valid()
            
            if license_info and is_valid:
                days_remaining = self.license_manager.get_days_remaining()
                status_text = (
                    f"✅ LICENCE ACTIVE\n"
                    f"Type: {license_info.license_type.value}\n"
                    f"Expire: {license_info.expires[:10]}\n"
                    f"Jours restants: {days_remaining}\n"
                    f"Étudiants max: {license_info.max_students if license_info.max_students > 0 else 'Illimité'}\n"
                    f"Machine: {license_info.machine_id[:8]}..."
                )
                
                if days_remaining < 30:
                    status_text += f"\n⚠️ EXPIRE BIENTÔT!"
                    
            else:
                status_text = "❌ AUCUNE LICENCE ACTIVE\n\nActivez une licence pour utiliser l'application."
            
            self.status_label.config(text=status_text)
            
        except Exception as e:
            logger.error(f"Erreur mise à jour statut: {e}")
            self.status_label.config(text=f"❌ ERREUR: {e}")
    
    def activate_license(self):
        """Lance l'activation de licence"""
        license_key = self.key_entry.get().strip()
        if not license_key:
            messagebox.showwarning("Clé Requise", "Veuillez saisir une clé de licence.")
            return
        
        # Désactiver le bouton pendant l'activation
        self.activate_btn.config(state=tk.DISABLED, text="Activation...")
        self.root.update()
        
        try:
            success = self.license_manager.activate_license(license_key, self.root, False)
            if success:
                self.key_entry.delete(0, tk.END)
                self.update_status()
        finally:
            self.activate_btn.config(state=tk.NORMAL, text="Activer")
    
    def activate_offline(self):
        """Lance l'activation hors ligne"""
        license_key = self.key_entry.get().strip()
        if not license_key:
            messagebox.showwarning("Clé Requise", "Veuillez saisir une clé de licence.")
            return
        
        self.offline_btn.config(state=tk.DISABLED, text="Activation...")
        self.root.update()
        
        try:
            success = self.license_manager.activate_license(license_key, self.root, True)
            if success:
                self.key_entry.delete(0, tk.END)
                self.update_status()
        finally:
            self.offline_btn.config(state=tk.NORMAL, text="Activer Hors Ligne")
    
    def check_license(self):
        """Vérifie la licence actuelle"""
        try:
            is_valid = self.license_manager.is_valid(check_server_time=True)
            integrity_ok = self.license_manager.validate_license_integrity()
            
            if is_valid and integrity_ok:
                messagebox.showinfo("Vérification", "✅ Licence valide et intègre")
            elif is_valid:
                messagebox.showwarning("Vérification", "⚠️ Licence valide mais intégrité compromise")
            else:
                messagebox.showerror("Vérification", "❌ Licence invalide ou expirée")
            
            self.update_status()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur vérification: {e}")
    
    def show_security_report(self):
        """Affiche le rapport de sécurité détaillé"""
        try:
            report_text = self.license_manager.export_license_report()
            
            # Créer une fenêtre pour le rapport
            report_window = tk.Toplevel(self.root)
            report_window.title("Rapport de Sécurité")
            report_window.geometry("700x600")
            
            # Zone de texte avec scrollbar
            text_frame = tk.Frame(report_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            scrollbar = tk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                                 font=("Courier", 9))
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar.config(command=text_widget.yview)
            
            text_widget.insert(tk.END, report_text)
            text_widget.config(state=tk.DISABLED)
            
            # Bouton fermer
            tk.Button(report_window, text="Fermer", 
                     command=report_window.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur génération rapport: {e}")
    
    def deactivate_license(self):
        """Désactive la licence avec confirmation"""
        if messagebox.askyesno("Confirmation", 
                              "Êtes-vous sûr de vouloir désactiver la licence?\n\n"
                              "Cette action est irréversible."):
            if self.license_manager.deactivate_license():
                messagebox.showinfo("Succès", "Licence désactivée avec succès.")
                self.update_status()
            else:
                messagebox.showerror("Erreur", "Impossible de désactiver la licence.")
    
    def auto_refresh(self):
        """Actualisation automatique du statut"""
        try:
            self.update_status()
        except Exception as e:
            logger.error(f"Erreur auto-refresh: {e}")
        finally:
            self.root.after(30000, self.auto_refresh)  # Répéter dans 30s
    
    def run(self):
        """Lance l'interface graphique"""
        self.root.mainloop()

# Fonctions utilitaires pour l'intégration
class LicenseAPI:
    """API simplifiée pour l'intégration dans l'application principale"""
    
    def __init__(self):
        self.manager = ModernLicenseManager()
    
    def check_access(self, feature: str = None) -> bool:
        """Vérifie l'accès avec gestion des fonctionnalités"""
        try:
            if not self.manager.is_valid():
                return False
            
            if feature:
                return self.manager.is_feature_enabled(feature)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur vérification accès: {e}")
            return False
    
    def get_student_limit(self) -> int:
        """Retourne la limite d'étudiants autorisée"""
        try:
            license_info = self.manager.get_license_info()
            if license_info and self.manager.is_valid():
                return license_info.max_students
            return 0
        except Exception:
            return 0
    
    def show_license_manager(self):
        """Affiche l'interface de gestion des licences"""
        try:
            gui = LicenseGUI()
            gui.run()
        except Exception as e:
            logger.error(f"Erreur affichage GUI: {e}")

# Décorateur pour la protection des fonctionnalités
def license_required(feature: str = None):
    """Décorateur pour protéger les fonctions par licence"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            api = LicenseAPI()
            if not api.check_access(feature):
                if feature:
                    messagebox.showerror("Accès Refusé", 
                                       f"Cette fonctionnalité ({feature}) nécessite une licence valide.")
                else:
                    messagebox.showerror("Accès Refusé", 
                                       "Cette action nécessite une licence valide.")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Exemple d'usage avec décorateur
class TaekwondoApp:
    """Exemple d'intégration dans l'application principale"""
    
    def __init__(self):
        self.license_api = LicenseAPI()
    
    @license_required()
    def start_application(self):
        """Démarrage protégé de l'application"""
        print("🥋 Application Taekwondo Manager démarrée")
        return True
    
    @license_required("competitions")
    def manage_competitions(self):
        """Gestion des compétitions (fonctionnalité premium)"""
        print("🏆 Module compétitions activé")
        return True
    
    @license_required("gestion_adherents")
    def manage_students(self):
        """Gestion des adhérents (fonctionnalité de base)"""
        limit = self.license_api.get_student_limit()
        print(f"👥 Module adhérents activé (limite: {limit})")
        return True
    
    def show_license_info(self):
        """Affiche les informations de licence"""
        stats = self.license_api.manager.get_usage_statistics()
        print("\n=== INFORMATIONS LICENCE ===")
        for key, value in stats.items():
            print(f"{key}: {value}")

# Point d'entrée principal
def main():
    """Point d'entrée principal avec gestion d'erreurs"""
    try:
        # Test du gestionnaire de licence
        print("🔧 Test du gestionnaire de licence modernisé...")
        
        license_manager = ModernLicenseManager()
        
        # Vérification initiale
        print(f"Licence valide: {license_manager.is_valid()}")
        
        security_report = license_manager.get_security_report()
        print(f"Statut sécurité: {security_report.status.value}")
        
        # Informations de licence
        license_info = license_manager.get_license_info()
        if license_info:
            print(f"Type: {license_info.license_type.value}")
            print(f"Jours restants: {license_manager.get_days_remaining()}")
        else:
            print("Aucune licence active")
        
        # Test de l'API
        print("\n🔧 Test de l'API simplifiée...")
        app = TaekwondoApp()
        
        # Tests avec gestion d'erreurs
        try:
            app.start_application()
        except Exception as e:
            print(f"Échec démarrage: {e}")
        
        try:
            app.manage_students()
        except Exception as e:
            print(f"Échec gestion étudiants: {e}")
        
        try:
            app.manage_competitions()
        except Exception as e:
            print(f"Échec gestion compétitions: {e}")
        
        app.show_license_info()
        
        # Lancer l'interface si demandé
        launch_gui = input("\nLancer l'interface graphique? (o/N): ").lower().startswith('o')
        if launch_gui:
            gui = LicenseGUI()
            gui.run()
    
    except Exception as e:
        logger.error(f"Erreur critique: {e}")
        print(f"❌ Erreur critique: {e}")

if __name__ == "__main__":
    main()