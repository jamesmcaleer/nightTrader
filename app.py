import datetime as dt
import yfinance as yf
import mplfinance as mpf
import time
import os
import email
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from pandas_datareader import data as pdr
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from PIL import Image

Base = declarative_base()

class Stock(Base):
   __tablename__ = "stocks"

   ticker = Column("ticker", String, primary_key=True)
   emails = Column("emails", String)

   def __init__(self, ticker, emails):
       self.ticker = ticker
       self.emails = emails

   def __repr__(self):
       return f"{self.ticker} {self.emails}"

engine = create_engine("sqlite:///mydb.db", echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

def db_main():
   # used for testing
   choice = input("Would you like to add a new (S)tock, (U)pdate, (R)emove, or (V)iew an object: ")
   if choice == 'S':
       ticker = input("ticker: ")
       emails = input("emails: ")
       session.add(Stock(ticker, emails))
   elif choice == 'U':
       ticker = input("ticker: ")
       item = input("item name: ")
       value = input("new value: ")
       type = input("int else string: ")
       setattr(session.query(Stock).filter_by(ticker=ticker).first(), item, int(value) if type == "int" else value)
   elif choice == 'R':
       ticker = input("ticker: ")
       session.delete(session.query(Stock).filter_by(ticker=ticker).first())
   elif choice == 'V':
       ticker = input("ticker: ")
       print(session.query(Stock).filter_by(ticker=ticker).first())

   session.commit()


def receive():
   system = 'night.trader.system@gmail.com'
   password = 'password'
   server = 'imap.gmail.com'

   # connect to the server and go to its inbox
   mail = imaplib.IMAP4_SSL(server)
   mail.login(system, password)
   # we choose the inbox but you can select others
   mail.select('inbox')

   # we'll search using the ALL criteria to retrieve
   # every message inside the inbox
   # it will return with its status and a list of ids
   status, data = mail.search(None, 'ALL')
   # the list returned is a list of bytes separated
   # by white spaces on this format: [b'1 2 3', b'4 5 6']
   # so, to separate it first we create an empty list
   mail_ids = []
   # then we go through the list splitting its blocks
   # of bytes and appending to the mail_ids list
   for block in data:
       # the split function called without parameter
       # transforms the text or bytes into a list using
       # as separator the white spaces:
       # b'1 2 3'.split() => [b'1', b'2', b'3']
       mail_ids += block.split()

   # now for every id we'll fetch the email
   # to extract its content
   for i in mail_ids:
       # the fetch function fetch the email given its id
       # and format that you want the message to be
       status, data = mail.fetch(i, '(RFC822)')

       # the content data at the '(RFC822)' format comes on
       # a list with a tuple with header, content, and the closing
       # byte b')'
       for response_part in data:
           # so if its a tuple...
           if isinstance(response_part, tuple):
               # we go for the content at its second element
               # skipping the header at the first and the closing
               # at the third
               message = email.message_from_bytes(response_part[1])

               # with the content we can extract the info about
               # who sent the message and its subject
               mail_from = message['from']
               mail_subject = message['subject']
               print(mail_from.split()[-1][1:-1])
               print(mail_subject)

def get_stock_data(stock, c):
   # get from 10 min ago to now
   end = dt.datetime.now() #+ dt.timedelta(hours=3, minutes=1) - dt.timedelta(days=1)  # maybe add 1 minute
   start = end - dt.timedelta(minutes=11)

   print(start, end)

   yf.pdr_override()
   df = pdr.get_data_yahoo(stock.ticker, start=start, end=end, interval="1m")
   print("df:")
   print(df)
   info = df["Close"][5:10]  # last 5 min of stocks
   print("last 5:")
   print(info)
   min = info.min()
   max = info.max()
   print("min: " + str(min))
   print("max: " + str(max))
   change = ((max - min) / min) * 100
   change = round(float(change), 2)
   print(change)

   # create graph
   if change > 2:
       prefix = stock.ticker + str(c)
       mpf.plot(df, type='candle', style='yahoo', savefig=prefix + ".png")
       image = prefix + ".png"
       send(stock, change, image, stock.emails.split())

def send(stock, change, image, recipients):
   with open(image, 'rb') as f:
       img_data = f.read()

   msg = MIMEMultipart()
   msg['Subject'] = stock.ticker + " has changed by " + str(change) + "%"
   system = 'night.trader.system@gmail.com'
   msg['From'] = system
   for email in recipients:
       msg['To'] = email

       text = MIMEText("test")
       msg.attach(text)
       image = MIMEImage(img_data, name=os.path.basename(image))
       msg.attach(image)

       s = smtplib.SMTP('smtp.gmail.com', 587)
       s.ehlo()
       s.starttls()
       s.ehlo()
       s.login(system, 'cndlgpvfgtisbttm')
       s.sendmail(system, email, msg.as_string())
       s.quit()

# round(float(percent_change), 2))
c = 1

def main():
   global c
   receive()
   # loops through each key of the stocks dictionary
   stocks = session.query(Stock).all()

   for stock in stocks:
       get_stock_data(stock, c)

   print(c)
   c += 1
   time.sleep(60)

stocks = session.query(Stock).all()

for stock in stocks:
   print(stock)

#for i in range(6):
   #db_main()
while True:
   main()

