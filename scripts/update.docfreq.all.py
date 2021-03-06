from configparser import RawConfigParser
from core.utils import PsqlAbstract, PsqlQuery

from core.ingest import PsqlIngester
from datetime import datetime
import time
import json
import logging


config_parser = RawConfigParser()
config_parser.read('../config.ini')

PsqlAbstract.set_database_info(
    config_parser.get('global', 'dbuser'),
    config_parser.get('global', 'dbname'),
    config_parser.get('global', 'dbpassword')
)


ingester = PsqlIngester('jieba')


logger = logging.getLogger('update.docfreq.all')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
chformatter = logging.Formatter('%(asctime)s [%(levelname)s] @%(filename)s: %(message)s', datefmt='[%d/%b/%Y %H:%M:%S]')
ch.setFormatter(chformatter)
logger.addHandler(ch)

def query_vocab_id(batch_size=1000):
    sql = 'SELECT id FROM pttcorpus_vocabulary;'
    psql = PsqlQuery()
    vocabs = psql.query(sql)
    batch = []
    i = 0
    for v in vocabs:
        batch.append(v[0])
        i += 1
        if i > batch_size:
            i = 0
            yield batch
            batch = []
    yield batch
    

if __name__ == '__main__':
    start = time.time()

    consumed = 0
    for vocab_ids in query_vocab_id(batch_size=1000):
        if len(vocab_ids) > 0:
            try:
                ingester.update_vocab_postfreq(vocab_ids)
                ingester.update_vocab_commentfreq(vocab_ids)
            except Exception as err:
                logger.error(vocab_ids)
                raise err

            consumed += len(vocab_ids)
            logger.info('{} vocab\'s docfreq are updated'.format(consumed))
    print('Elapsed time @update_docfreq: {:.2f}sec.'.format(time.time() - start))

