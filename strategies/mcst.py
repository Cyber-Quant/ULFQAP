from strategies.common import get_liqa_share


class MCSTInfo:
    def __init__(self):
        self.name = '市场平均成本'
        self.desc = '''
        成交量(手)/当前流通股本(手)为权重成交额(元)/(100*成交量(手))的动态移动平均
        '''
        self.choose_flag = False
        self.watch_flag = False


class MCST:
    def __init__(self):
        pass

    def calc_batch_mcst(self, volumes, amount, code):
        mcst = []
        # FIXME get different liqa_share by date.
        liqa_share = get_liqa_share(code)
        for i, _ in enumerate(volumes):
            if volumes[i] == 0:
                _mcst = 0
            elif liqa_share == 0:
                _mcst = 0
            else:
                # _mcst = (volumes[i] / liqa_share) * amount[i] / volumes[i] / 100
                _mcst = (volumes[i] / liqa_share) * amount[i] / volumes[i]
            mcst.append(_mcst)
        return mcst
