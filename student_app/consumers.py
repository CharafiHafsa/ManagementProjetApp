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