import json
import os
import re
from typing import TextIO, List, Union

from flask import Flask, request
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def exec_commands(query: str, file: TextIO) -> Union[List[str], BadRequest]:
    cmds = list( map( lambda v: v.strip(), query.split('|')) )
    res = list( map( lambda v: v.strip(), file) )
    print(res)

    for cmnd in cmds:
        words = cmnd.split(':')

        if words[0] == "filter":
            res = list( filter( lambda v: words[1] in v, res) )
        elif words[0] == "map":
            res = list( map( lambda v: v.split(' ')[int(words[1])], res) )
        elif words[0] == "sort":
            res = sorted( res, reverse= words[1] == "desc" )
        elif words[0] == "limit":
            res = list(res)[:int(words[1])]
        elif words[0] == "unique":
            res = list( set(res) )
        elif words[0] == "regex":
            regex = re.compile(rf"{words[1]}")
            res_1 = []
            for item in res:
                if regex.search(item):
                    print(item)
                    res_1.append(item)
            res = res_1



        else:
            return BadRequest(description=f"Command {'|'.join(words)} not found")

    return res


@app.post("/perform_query")
def perform_query() -> List[str]:
    # нужно взять код из предыдущего ДЗ
    # добавить команду regex
    # добавить типизацию в проект, чтобы проходила утилиту mypy app.py

    try:
        data = json.loads( request.data )
        print(data)
        query = data["query"]
        file_name = data["file_name"]
    except KeyError:
        raise BadRequest(description=f"File {file_name} not found")

    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):
        raise BadRequest(description=f"File {file_name} not found")


    with open(file_path) as f:
        res = "\n".join( exec_commands(query, f) )
        # print(res)

    return res


app.run()
