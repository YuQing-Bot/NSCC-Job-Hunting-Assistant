import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import threading
import os

# Set URL
url = "https://www.careerbeacon.com/en/search?filter-company_id=205855"

# Define a flag variable to control the refresh loop
refresh_flag = True

def clear_screen():
    # Clears the screen according to the operating system
    os.system('cls' if os.name == 'nt' else 'clear')

def print_all_jobs():
    while refresh_flag:
        clear_screen()  # Clears the screen
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            job_elements = soup.find_all("div", class_="non_featured_job_container")
            for job in job_elements:
                title_element = job.find("a", class_="serp_job_title")
                date_element = job.find("div", class_="smaller text-muted")
                if title_element and date_element:
                    title = title_element.text.strip()
                    date_str = date_element.get("title", "")
                    if date_str:
                        posted_date = datetime.strptime(date_str, "%Y-%m-%d")
                        days_ago = (datetime.now() - posted_date).days
                        print(f"Job Title: {title}\nPosted: {date_str} ({days_ago} days ago)\n")
                    else:
                        print(f"Job Title: {title}\nPosted date: Unknown\n")
        else:
            print("Failed to retrieve the webpage")
        
        # count down
        for i in range(1800, 0, -1):
            print(f"Refreshing in {i} seconds...", end='\r')
            time.sleep(1)

def monitor_specific_jobs(keywords):
    while refresh_flag:
        clear_screen()  # Clears the screen
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            job_elements = soup.find_all("div", class_="non_featured_job_container")
            for job in job_elements:
                title_element = job.find("a", class_="serp_job_title")
                if title_element:
                    title = title_element.text.strip()
                    for keyword in keywords:
                        if keyword.lower() in title.lower():
                            print(f"Found a matching job: {title}\n")
                            break
        else:
            print("Failed to retrieve the webpage")
        
        # count down
        for i in range(1800, 0, -1):
            print(f"Refreshing in {i} seconds...", end='\r')
            time.sleep(1)

def stop_refresh():
    global refresh_flag
    while True:
        user_input = input()
        if user_input == '0':
            refresh_flag = False
            break

def main():
    choice = input("Enter 1 to print all job positions, or 2 to search for specific positions and monitor in real time: ")
    if choice == '1':
        # Start a thread to execute the print_all_jobs function
        refresh_thread = threading.Thread(target=print_all_jobs)
        refresh_thread.start()
    elif choice == '2':
        keywords = input("Enter the keywords for the job positions you want to monitor (separated by commas): ").split(',')
        # Start a thread to execute the monitor_specific_jobs function
        refresh_thread = threading.Thread(target=lambda: monitor_specific_jobs(keywords))
        refresh_thread.start()
    else:
        print("Invalid choice. Please enter 1 or 2.")
        return

    # Start another thread to execute the stop_refresh function
    stop_thread = threading.Thread(target=stop_refresh)
    stop_thread.start()

    # Wait for both threads to finish
    refresh_thread.join()
    stop_thread.join()

if __name__ == "__main__":
    main()