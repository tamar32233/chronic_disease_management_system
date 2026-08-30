#import pika so we can work with rabbitMQ- in this project Flask does not do the analysis or the visualization
#It just sends them via rabbitMQ
import pika
#we use json to send structured data through RabbitMQ.
import json
#import flask that will create a small API that will enable us to send messages via browser.
from flask import Flask
#here we create the flask app itself.
app = Flask(__name__)


#when someone enters this v URL, run the following function.
#this is a route for the statistics tasks.
@app.route("/statistics/<task>")
#this following function is sending statistics tasks to rabbitMQ
def send_statistics_task(task):
    #open a regular synchronous connection to rabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    #now we create a channel, and all the functions will be done via this channel
    channel = connection.channel()
    #Declare the queue that will receive statistics tasks.
    #The actual routing is done by RabbitMQ through the exchange and routing key.
    channel.queue_declare(queue='statistics_queue')
    #the info that is sent to the consumer:
    message = {"task": task}
    #here we send the message to rabbitMQ
    #basic publish sends the messages.
    channel.basic_publish(
        exchange='tasks_exchange',
        routing_key='statistics',
        body=json.dumps(message))
    #close the connection after use. (to avoid memory leaks for example)
    connection.close()
    #flask returns the text to the browser
    return f"Sent task: {task}"





#now we do the same for visualizations:
@app.route("/visualizations/<task>")
def send_visualizations_task(task):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))

    channel = connection.channel()
    channel.queue_declare(queue='visualizations_queue')
    message = {"task": task}
    channel.basic_publish(
        exchange='tasks_exchange',
        routing_key='visualizations',
        body=json.dumps(message))
    connection.close()
    return f"Sent task: {task}"


#checks if this file is running directly.
#if it does, flask will begin to run
#if the file is being imported from another file, this code won't run.
if __name__ == "__main__":
    #flask activates the localhost
    app.run(debug=True)



