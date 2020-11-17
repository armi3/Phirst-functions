from google.cloud import pubsub

publisher = pubsub.PublisherClient()
project_id = 'phirst-e425b'
topic_id = 'pitchfork-takes'
topic_path = publisher.topic_path(project_id, topic_id)


def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    # request_json = request.get_json()
    # if request.args and 'message' in request.args:
    #     return request.args.get('message')
    # elif request_json and 'message' in request_json:
    #     return request_json['message']
    # else:
    #     return f'Hello World!'

    # try:
    #     test_attribute = request.get_json().get('test')
    #     # topic_name = 'projects/phirst-e425b/topics/pitchfork-takes'.format(
    #     #     project_id=project_id,
    #     #     topic=topic_id,
    #     # )
    #     future = publisher.publish(topic_path, "Hay nuevo hot take, actualizar!!".encode("utf-8"))
    #     print(future.result())
    #     print(f"Published messages to {topic_path}.")
    #     return f"OK"
    # except:
    #     return f"Not OK"
    future = publisher.publish(topic_path, "Hay nuevo hot take, actualizar!!".encode("utf-8"))
    print(future.result())
    print(f"Published messages to {topic_path}.")
    return f"OK"
