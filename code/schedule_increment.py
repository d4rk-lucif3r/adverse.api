from incremental import *
import schedule
import time

def job():
	print("Running Batch Table")
	run_batch()
    # print("I'm working...")

# schedule.every(10).minutes.do(job)
# schedule.every().hour.do(job)
# schedule.every().day.at("10:30").do(job)
# DON"T FORGET TO CHANGE DAY AND TIME
schedule.every().tuesday.at("03:49").do(job)
# schedule.every().wednesday.at("13:15").do(job)
# schedule.every().minute.at(":17").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
