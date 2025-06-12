import json
from channels.generic.websocket import AsyncWebsocketConsumer
from base_de_donnee.models import Message, Etudiant, Groupe
from django.utils.timezone import now
from channels.db import database_sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from base_de_donnee.models import Message, Etudiant, Groupe
from django.utils.timezone import now
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.groupe_id = None  # Initialiser l'ID du groupe
        self.room_group_name = None

        await self.accept()

    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        try:
            if data['action'] == 'join':
                self.groupe_id = data['groupe_id']
                self.room_group_name = f"chat_{self.groupe_id}"
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                print(f"✅ Connexion établie pour le groupe {self.groupe_id}")

            elif data['action'] == 'send_message':
                message = data['message']
                etudiant_id = data['etudiant_id']
                # Récupération de l'étudiant et du groupe
                etudiant = await database_sync_to_async(Etudiant.objects.get)(id=etudiant_id)
                groupe = await database_sync_to_async(Groupe.objects.get)(id=self.groupe_id)
                # Enregistrement du message dans la base de données
                msg = await database_sync_to_async(Message.objects.create)(
                    contenu=message,
                    etudiant=etudiant,
                    groupe=groupe,
                    date_envoi=now()
                )
                # Envoi du message à tous les utilisateurs connectés dans le groupe
                # On évite ici l'appel à "photo_profil"
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'etudiant_nom': etudiant.nom,
                        'etudiant_id': etudiant.id,
                        'date_envoi': msg.date_envoi.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                )
        except Exception as e:
            print("Erreur dans le consumer :", e)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.groupe_id = None  # Initialiser l'ID du groupe
        self.room_group_name = None

        await self.accept()

    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
            data = json.loads(text_data)
            try:
                action = data.get('action')
                
                # Gestion de la connexion au groupe
                if action == 'join':
                    self.groupe_id = data['groupe_id']
                    self.room_group_name = f"chat_{self.groupe_id}"
                    await self.channel_layer.group_add(
                        self.room_group_name,
                        self.channel_name
                    )
                    print(f"✅ Connexion établie pour le groupe {self.groupe_id}")

                # Gestion de l'envoi de message (inchangé)
                elif action == 'send_message':
                    message = data['message']
                    etudiant_id = data['etudiant_id']
                    # Récupération de l'étudiant et du groupe
                    etudiant = await database_sync_to_async(Etudiant.objects.get)(id=etudiant_id)
                    groupe = await database_sync_to_async(Groupe.objects.get)(id=self.groupe_id)
                    # Enregistrement du message dans la base de données
                    msg = await database_sync_to_async(Message.objects.create)(
                        contenu=message,
                        etudiant=etudiant,
                        groupe=groupe,
                        date_envoi=now()
                    )
                    # Envoi du message à tous les utilisateurs connectés dans le groupe
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': message,
                            'etudiant_nom': etudiant.nom,
                            'etudiant_id': etudiant.id,
                            'date_envoi': msg.date_envoi.strftime('%Y-%m-%d %H:%M:%S'),
                        }
                    )
                    
                # Gestion des mises à jour Meet (améliorée)
                elif action == 'meet_update':
                    groupe_id = data['groupe_id']
                    meet_action = data['meet_action']  # 'started' ou 'ended'
                    meet_link = data.get('meet_link', '')
                    
                    # Validation des données
                    if groupe_id != self.groupe_id:
                        raise ValueError("ID de groupe incompatible")
                        
                    if meet_action not in ['started', 'ended']:
                        raise ValueError("Action Meet non valide")
                    
                    # Mise à jour du statut du meet dans la base de données
                    update_success = await self.update_meet_status(groupe_id, meet_link if meet_action == 'started' else '')
                    
                    if not update_success:
                        raise ValueError("Échec de la mise à jour du statut Meet")
                    
                    # Diffuser la mise à jour à tous les membres du groupe
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'meet_update',
                            'groupe_id': groupe_id,
                            'action': meet_action,
                            'meet_link': meet_link,
                            'timestamp': now().isoformat(),  # Ajout d'un timestamp
                        }
                    )
                    
                else:
                    print(f"Action non reconnue: {action}")
                    
            except KeyError as e:
                print(f"Erreur de clé manquante dans les données: {e}")
            except ValueError as e:
                print(f"Erreur de validation: {e}")
            except Exception as e:
                print(f"Erreur inattendue dans le consumer: {str(e)}")
                # Envoyer un message d'erreur au client si nécessaire
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Une erreur est survenue'
                }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
    
    # Nouvelle méthode pour envoyer les mises à jour de meet
    async def meet_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'meet_update',
            'groupe_id': event['groupe_id'],
            'action': event['action'],
            'meet_link': event['meet_link']
        }))
    
    # Méthode pour mettre à jour le statut du meet dans la base de données
    @database_sync_to_async
    def update_meet_status(self, groupe_id, meet_link):
        try:
            groupe = Groupe.objects.get(id=groupe_id)
            groupe.meet_link = meet_link
            groupe.save()
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour du statut du meet: {e}")
            return False