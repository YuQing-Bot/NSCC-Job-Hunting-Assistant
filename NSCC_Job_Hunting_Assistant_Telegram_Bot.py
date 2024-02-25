import nest_asyncio
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Apply the nest_asyncio patch to enable nested event loops
nest_asyncio.apply()

# Set the target URL
url = "https://www.careerbeacon.com/en/search?filter-company_id=205855"

# Global variable to control the monitoring task
monitor_task = None

async def print_all_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = ""
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        job_elements = soup.find_all("div", class_="non_featured_job_container")
        for job in job_elements:
            title_element = job.find("a", class_="serp_job_title")
            date_element = job.find("div", class_="smaller text-muted")
            if title_element and date_element:
                title = title_element.text.strip()
                link = title_element.get('href')  # Get the job details link
                date_str = date_element.get("title", "")
                if date_str:
                    posted_date = datetime.strptime(date_str, "%Y-%m-%d")
                    days_ago = (datetime.now() - posted_date).days
                    message += f"Job Title: {title}\nLink: {link}\nPosted: {date_str} ({days_ago} days ago)\n\n"
                else:
                    message += f"Job Title: {title}\nLink: {link}\nPosted date: Unknown\n\n"
    else:
        message = "Failed to retrieve the webpage"

    if message:
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("No jobs found.")

async def monitor_specific_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global monitor_task
    keywords = context.args

    await update.message.reply_text("Starting job monitoring...")

    async def monitor():
        while True:
            message = ""
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                job_elements = soup.find_all("div", class_="non_featured_job_container")
                for job in job_elements:
                    title_element = job.find("a", class_="serp_job_title")
                    if title_element:
                        title = title_element.text.strip()
                        link = title_element.get('href')  # Get the job details link
                        for keyword in keywords:
                            if keyword.lower() in title.lower():
                                message += f"Found a matching job:\nJob Title: {title}\nLink: {link}\n\n"
                                break
            else:
                message = "Failed to retrieve the webpage"

            if message:
                await update.message.reply_text(message)
            else:
                await update.message.reply_text("No matching jobs found at this moment.")

            print("Monitoring... waiting for next check.")
            await asyncio.sleep(3600)  # Latest data from website every 30 minutes

    monitor_task = asyncio.create_task(monitor())

async def cancel_monitoring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global monitor_task
    if monitor_task and not monitor_task.done():
        monitor_task.cancel()
        await update.message.reply_text("Monitoring has been cancelled.")
    else:
        await update.message.reply_text("Monitoring is not active or already cancelled.")

async def main():
    # Create the Telegram bot application
    application = Application.builder().token("YOUR_BOT_KEY").build()

    # Add command handlers
    application.add_handler(CommandHandler("alljobs", print_all_jobs))
    application.add_handler(CommandHandler("monitor", monitor_specific_jobs))
    application.add_handler(CommandHandler("cancel", cancel_monitoring))

    # Run the bot using the asyncio event loop
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())