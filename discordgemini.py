import os
import discord
import asyncio
from google import genai

# Configurar la API de Gemini
env_vars = {key: os.getenv(key) for key in ['DISCORD_TOKEN', 'GEMINI_API_KEY']}
DISCORD_TOKEN = env_vars['DISCORD_TOKEN']
GEMINI_API_KEY = env_vars['GEMINI_API_KEY']

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Habilitar acceso a contenido de mensajes

client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1alpha'})
model_id = "gemini-2.0-flash-exp"
config = {
    "response_modalities": ["TEXT"],
    "max_tokens": 500,  # Aumentar el límite de tokens para respuestas más largas
    "temperature": 0.7
}

class ChatBot(discord.Client):
    async def on_ready(self):
        print(f'{self.user} is connected to Discord!')

    async def on_message(self, message):
        if message.author == self.user:
            return

        print(f"Received message: {message.content}")

        if not message.content.startswith('!'):
            return

        input_content = message.content[1:]  # Eliminar el signo de admiración
        prompt = f"Eres un bot de Discord. Responde de manera concisa y no muy extendida. Pregunta: {input_content}"
        print(f"Sending to Gemini API: {prompt}")

        try:
            async with client.aio.live.connect(model=model_id, config=config) as session:
                await session.send(input_content, end_of_turn=True)

                full_response = ""
                async for response in session.receive():
                    part_text = response.text.strip() if response.text else ""
                    full_response += part_text
                    print(f"Received response part: {part_text}")

                if full_response:  # Verificar respuesta acumulada no vacía
                    print(f"Full response: {full_response}")
                    await message.channel.send(full_response)
                else:
                    print("La respuesta está vacía o no válida.")
        except Exception as e:
            print(f"Error en comunicación con Gemini API: {e}")

bot = ChatBot(intents=intents)

if __name__ == "__main__":
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"Error al iniciar el bot: {e}")

# aa