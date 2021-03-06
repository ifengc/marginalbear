from configparser import RawConfigParser
import sys
from core.utils import PsqlAbstract, clean_query
from core.chat import RetrievalEvaluate
from core.tokenizer import (
    JiebaTokenizer,
    OpenCCTokenizer
)


config_parser = RawConfigParser()
config_parser.read('../config.ini')

PsqlAbstract.set_database_info(
    config_parser.get('global', 'dbuser'),
    config_parser.get('global', 'dbname'),
    config_parser.get('global', 'dbpassword')
)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(
            '''
            usage: python query_chat <query-string>
            ex: python query_chat 安安幾歲住哪
            '''
        )
        sys.exit(0)
    raw = sys.argv[1]
    query, ctype = clean_query(raw)
    words = [w for w in OpenCCTokenizer(JiebaTokenizer()).cut(query) if bool(w.word.strip())]
    print(words)
    comments = RetrievalEvaluate('ccjieba').retrieve(words)
    # response = comment.body

    for i, cmt in enumerate(comments, 1):
        print('[{}] <{:.2f}> {}'.format(i, cmt.score, cmt.body))

