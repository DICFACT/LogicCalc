"""Толчка старта программы"""
import argparse

from core import const

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='scaling', type=float, default=1, help='Scaling of the gui')
    args = parser.parse_args()
    const.SCALING = args.scaling
    const.recalculate_screen_size()

    from core.logic_calc import LogicCalc
    LogicCalc.run()
