from api_call import data_call
import logging
import time

def main():
    logging.info("Starting API call loop...")
    while True:
        appended_columns = data_call()
        
        time.sleep(15)

if __name__ == "__main__":
    main()