import time
import numpy as np
from datetime import datetime, timedelta

from pathlib import Path
from contextlib import contextmanager

class Log:
    def __init__(self, msg=None, filename='', output='screen'):
        self.filename = filename
        self.output_file = True if output in ['file', 'both'] else False
        self.output_screen = True if output in ['screen', 'both'] else False
        self.start_time = time.time()

        if msg:
            self._output(msg)

    def stop(self, msg=None):
        m, s = divmod(time.time()-self.start_time, 60)
        h, m = divmod(m, 60)

        if msg:
            self._output(msg)

        self._output('Total time: {:d}:{:02d}:{:02d}.{:d}'.format(
            int(h), int(m), int(s), int((s-int(s))*10000)
        ))

    def log(self, msg):
        self._output(msg)

    def _output(self, msg):
        output = '{:} - {:}'.format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            msg
        )

        if (self.output_file):
            f = open(self.filename, "a")
            f.write(output + '\n')
            f.close()

        if (self.output_screen):
            print(output)

    @staticmethod
    @contextmanager
    def save_file(path, timestamp="%Y%m%d%H%M"):
        path = Path(path)
        filename = path.with_name(
            f"{path.stem}_{datetime.now():{timestamp}}{path.suffix}"
        )

        yield filename

        print(
            "File saved to `{:}` ({:})".format(
                filename,
                Formatter.byte_number_format(filename.stat().st_size)
            )
        )
    
    # with Log.save_file("output/gold_dataset_ragflow_relevance.csv") as filename:
    #   pdf_data.to_csv(filename, sep="\t", index=False)

class Memory:
    @staticmethod
    def reduce_mem_usage(pdf_data, verbose=True):
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        start_mem = pdf_data.memory_usage(index=True, deep=True).sum() / 1024**2
        if verbose:
            print('Starting memory usage: {:5.2f} MB'.format(start_mem))

        for col in pdf_data.columns:
            col_type = pdf_data[col].dtypes

            if col_type in numerics:
                c_min = pdf_data[col].min()
                c_max = pdf_data[col].max()

                if str(col_type)[:3] == 'int':
                    if c_min >= np.iinfo(np.int8).min and c_max <= np.iinfo(np.int8).max:
                        pdf_data[col] = pdf_data[col].astype(np.int8)
                    elif c_min >= np.iinfo(np.int16).min and c_max <= np.iinfo(np.int16).max:
                        pdf_data[col] = pdf_data[col].astype(np.int16)
                    elif c_min >= np.iinfo(np.int32).min and c_max <= np.iinfo(np.int32).max:
                        pdf_data[col] = pdf_data[col].astype(np.int32)
                    elif c_min >= np.iinfo(np.int64).min and c_max <= np.iinfo(np.int64).max:
                        pdf_data[col] = pdf_data[col].astype(np.int64)  
                else:
                    if c_min >= np.finfo(np.float16).min and c_max <= np.finfo(np.float16).max:
                        pdf_data[col] = pdf_data[col].astype(np.float16)
                    elif c_min >= np.finfo(np.float32).min and c_max <= np.finfo(np.float32).max:
                        pdf_data[col] = pdf_data[col].astype(np.float32)
                    else:
                        df[col] = df[col].astype(np.float64)    
        end_mem = pdf_data.memory_usage(index=True, deep=True).sum() / 1024**2
        if verbose:
            print('Reduced memory usage: {:5.2f} MB ({:.1f}% reduction)'.format(
                end_mem,
                100 * (start_mem - end_mem) / start_mem)
            )
        return pdf_data

    @staticmethod
    def get_memory_usage(obj):
        import sys
        from types import ModuleType, FunctionType
        from gc import get_referents

        BLACKLIST = type, ModuleType, FunctionType

        if isinstance(obj, BLACKLIST):
            raise TypeError('getsize() does not take argument of type: '+ str(type(obj)))
        seen_ids = set()
        size = 0
        objects = [obj]
        while objects:
            need_referents = []
            for obj in objects:
                if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                    seen_ids.add(id(obj))
                    size += sys.getsizeof(obj)
                    need_referents.append(obj)
            objects = get_referents(*need_referents)
        return size

class Formatter:
    @staticmethod
    def clean_query(str_template):
        import re

        print(
            re.sub(
                ' +',
                ' ',
                re.sub(
                    '\n',
                    ' ',
                    re.sub('^( {4}--.*)$', '', str_template, flags=re.MULTILINE),
                    flags=re.MULTILINE
                ),
                flags=re.MULTILINE
            )
        )

    @staticmethod
    def byte_number_format(num, suffix='B'):
        for unit in ['','K','M','G','T','P','E','Z']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0

        return "%.1f%s%s" % (num, 'Y', suffix)

    @staticmethod
    def decimal_number_format(num):
        for unit in ['','k','M','B']:
            if abs(num) < 1000.0:
                return "%3.1f%s" % (num, unit)
            num /= 1000.0

        return "%.1f%s" % (num, 'T')