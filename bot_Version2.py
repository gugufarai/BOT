import asyncio
import random
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ========= CONFIG =========
TOKEN = "SEU_TOKEN_AQUI"
CANAL_VIP = "@seu_canal_vip"
ADMIN_ID = 123456789
INTERVALO_MINUTOS = 5

# ========= CONTROLE =========
bot_ativo = False
historico = []
stats = {"win": 0, "loss": 0}

# ========= GERAR DADOS (DEMO) =========
def gerar_dados(qtd=2000):
    dados = []
    for _ in range(qtd):
        seq = [random.choice([0, 1]) for _ in range(5)]
        resultado = 1 if seq.count(1) > seq.count(0) else 0
        dados.append(seq + [resultado])
    return dados

# ========= TREINAR IA =========
dados = gerar_dados()
df = pd.DataFrame(dados, columns=["r1","r2","r3","r4","r5","resultado"])
X = df.drop("resultado", axis=1)
y = df["resultado"]

modelo = RandomForestClassifier(n_estimators=100)
modelo.fit(X, y)

print("🤖 IA treinada (DEMO)")

# ========= IA PREVISÃO =========
def prever_sinal():
    if len(historico) < 5:
        return "🟥 Banker"

    entrada = historico[-5:]
    pred = modelo.predict([entrada])[0]
    return "🟦 Player" if pred == 1 else "🟥 Banker"

# ========= LOOP DE SINAIS =========
async def loop_sinais(app):
    global bot_ativo

    while True:
        if bot_ativo:
            sinal = prever_sinal()
            agora = datetime.now().strftime("%H:%M")

            mensagem = (
                "🎯 **SINAL BAC BO (IA)**\n\n"
                f"{sinal}\n"
                "⏱ Entrar agora\n"
                "🟢 Proteção: Empate\n"
                "🔁 Até 2 Gales\n\n"
                f"🕒 {agora}"
            )

            await app.bot.send_message(
                chat_id=CANAL_VIP,
                text=mensagem,
                parse_mode="Markdown"
            )

            # resultado SIMULADO
            resultado_real = random.choice([0, 1])
            entrada_num = 1 if "Player" in sinal else 0
            historico.append(resultado_real)

            if entrada_num == resultado_real:
                stats["win"] += 1
            else:
                stats["loss"] += 1

        await asyncio.sleep(INTERVALO_MINUTOS * 60)

# ========= COMANDOS =========
async def ligar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_ativo
    if update.effective_user.id == ADMIN_ID:
        bot_ativo = True
        await update.message.reply_text("✅ Bot LIGADO")

async def parar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_ativo
    if update.effective_user.id == ADMIN_ID:
        bot_ativo = False
        await update.message.reply_text("⛔ Bot PARADO")

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = stats["win"] + stats["loss"]
    taxa = (stats["win"] / total * 100) if total > 0 else 0

    texto = (
        "📊 **ESTATÍSTICAS**\n\n"
        f"✅ Wins: {stats['win']}\n"
        f"❌ Loss: {stats['loss']}\n"
        f"📈 Assertividade: {taxa:.2f}%"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")

# ========= MAIN =========
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("ligar", ligar))
    app.add_handler(CommandHandler("parar", parar))
    app.add_handler(CommandHandler("stats", stats_cmd))

    asyncio.create_task(loop_sinais(app))
    print("🚀 Bot iniciado")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())