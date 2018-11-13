def error_msg_from_exception(e):
    """Translate exception into error message

    Database have different ways to handle exception. This function attempts
    to make sense of the exception object and construct a human readable
    sentence.

    TODO(bkyryliuk): parse the Presto error message from the connection
                     created via create_engine.
    engine = create_engine('presto://localhost:3506/silver') -
      gives an e.message as the str(dict)
    presto.connect("localhost", port=3506, catalog='silver') - as a dict.
    The latter version is parsed correctly by this function.
    """
    msg = ''
    if hasattr(e, 'message'):
        if type(e.message) is dict:
            msg = e.message.get('message')
        elif e.message:
            msg = "{}".format(e.message)
    return msg or '{}'.format(e)
