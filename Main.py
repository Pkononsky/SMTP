import base64
import os
import re
import socket
import ssl

FROM = "" #email
PASSWD = ""  #пароль
TO = ""
SUBJECT = ""
FILES = ""
TEXT = ""

recv_bytes = 10000


def parse_conf():
    global FROM, PASSWD, TO, SUBJECT, FILES
    file = open("conf.txt", mode="r")
    conf = file.read()
    try:
        TO = re.search(r"To: (.+)", conf).group(1)
        SUBJECT = re.search(r"Subject: (.+)", conf).group(1)
        files_res = re.search(r"File Names: (.+)", conf)
        if files_res is not None:
            FILES = files_res.group(1)
    except:
        print("Ошибка в конфигурационном файле")
        os.abort()


def get_message():
    global TEXT
    file = open("mail.txt", mode="r", encoding="utf-8")
    TEXT = file.read()


def prepare_connection(sock):
    sock.recv(recv_bytes)
    sock.send(b"EHLO good_girl\r\n")
    sock.recv(recv_bytes)
    sock.send(b"AUTH LOGIN\r\n")
    sock.recv(recv_bytes)
    soap64 = base64.b64encode(FROM.encode()) + b"\r\n"
    passwd64 = base64.b64encode(PASSWD.encode()) + b"\r\n"
    sock.send(soap64)
    sock.recv(recv_bytes)
    sock.send(passwd64)
    sock.recv(recv_bytes)

    sock.send(b"MAIL FROM:<%s>\r\n" % (FROM.encode()))
    sock.recv(recv_bytes)
    sock.send(b"RCPT TO:<%s>\r\n" % (TO.encode()))
    sock.recv(recv_bytes)


def add_attachments(sock):
    for i in FILES.split(", "):
        if i.replace(" ", "") == "":
            continue
        sock.send(b"--sep\r\n")
        sock.send(b"Content-type: multipart/mixed\r\n")
        sock.send(b"Content-Transfer-Encoding: base64\r\n")
        sock.send(b'Content-Disposition: attachment; filename="%s"\r\n' % i.encode())
        sock.send(b"\r\n")
        file = open(i.encode(), mode="rb")
        data = file.read()
        sock.sendall(base64.b64encode(data) + b"\n\r")
        sock.send(b"\r\n")


def send_mesage(sock):
    sock.send(b"DATA\r\n")
    sock.recv(recv_bytes)
    sock.send(b"From: %s <%s>\r\n" % (FROM.encode(), FROM.encode()))
    sock.send(b"Subject: %s\r\n" % SUBJECT.encode())
    sock.send(b"To: %s\r\n" % TO.encode())
    sock.send(b"Date: 27 Aug 17 1945\r\n")
    sock.send(b"Content-type: multipart/mixed; boundary=sep\r\n")
    sock.send(b"\r\n")
    sock.send(b"--sep\r\n")
    sock.send(b"Content-type: text/plain; charset=utf-8\r\n")
    sock.send(b"\r\n")
    sock.send(b"%s\r\n" % TEXT.encode())
    add_attachments(sock)
    sock.send(b".\r\n")
    print(sock.recv(recv_bytes))
    sock.send(b"QUIT\r\n")
    print(sock.recv(recv_bytes))


def check_connection_to_network():
    try:
        sock = socket.socket()
        sock.connect(("google.com", 80))
        sock.close()
    except:
        print("Нет подключения к Интернету")
        os.abort()


if __name__ == '__main__':
    check_connection_to_network()
    parse_conf()
    get_message()

    contex = ssl.create_default_context()
    s = socket.socket()
    s.connect(("smtp.yandex.ru", 465))
    sock = contex.wrap_socket(s, server_hostname="smtp.yandex.ru")

    prepare_connection(sock)
    send_mesage(sock)

    s.close()
    sock.close()
