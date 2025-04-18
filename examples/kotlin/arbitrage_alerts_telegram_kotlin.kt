import com.solana.mvp.ArbitrageScanner
import com.github.kotlintelegrambot.Bot
import com.github.kotlintelegrambot.bot

fun main() {
    val scanner = ArbitrageScanner(listOf("Raydium", "Orca", "Jupiter"))
    val bot = Bot.Builder().token("YOUR_TELEGRAM_TOKEN").build()

    scanner.onOpportunity { detail ->
        bot.sendMessage(chatId = ChatId.fromId(123456789), text = "Arbitrage opportunity: $detail")
    }
    scanner.start()
}
