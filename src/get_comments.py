import asyncio
import json
from telethon.sync import TelegramClient
from telethon.sessions import MemorySession
from telethon.tl.functions.channels import GetFullChannelRequest

# Replace these with your own API credentials
api_id = input()
api_hash = input()
channel_username = input()#'zedigital'


post_id = int(input())#3020

all_messages = []

async def main():
    async with TelegramClient(MemorySession(), api_id, api_hash) as client:
        channel = await client.get_entity(channel_username)
        full_channel = await client(GetFullChannelRequest(channel))

        # Check if there's a linked group for comments
        if full_channel.full_chat.linked_chat_id:
            linked_group = await client.get_entity(full_channel.full_chat.linked_chat_id)
            print(f'Linked Group: {linked_group.title}')

            # Find the message in the linked group that corresponds to the post_id
            async for message in client.iter_messages(linked_group):

                    async for comment in client.iter_messages(linked_group, limit=1035, reply_to=message.id):
                        print(f'Comment ID: {comment.id}\nComment Content: {comment.text}\n')
                        all_messages.append(comment.text)
                    
                    break

        else:
            print('No linked group for comments found.')

asyncio.run(main())

with open('data/messages.json', 'w') as f:
    json.dump({'messages': all_messages}, f)