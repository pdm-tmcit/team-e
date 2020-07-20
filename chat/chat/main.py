from interface import interface

def build_prompt(interface):
    return '{name}:{responder} > '.format(name=interface.name,responder=interface.responder_name)


if __name__ == '__main__':

    print('this is prototype system')
    proto = interface('proto')
    while True:
        text = input('>')
        if not text:
            break

        try:
            response = proto.dialogue(text)
        except IndexError as error:
            print('{}: {}'.format(type(error).__name__, str(error)))
            print('警告: 辞書が空です。(Responder: {})'.format(proto.responder_name))
        else:
            print('{prompt}{response}'.format(prompt=build_prompt(proto),
                                                  response=response))
    proto.save()
