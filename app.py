"""
    FinoAPI —— 活动小程序「FinoLab 现象实验室」的后端服务程序
    Backend Service Program for the Wechat Miniprogram 'FinoLab - Phenomenon Laboratory'

    2024年，Daaihang（Hiroaki）Wong 版权所有
    Copyright (C) 2024 Daaihang "Hiroaki" Wong

    此程序是自由软件：您可以根据自由软件基金会发布的 GNU 通用公共许可证的条款
    重新分发和/或修改它，无论是许可证的第 3 版，还是（由您选择的）任何更高版本。
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    分发此程序是希望它有所用之处，但 **不提供任何保证**；
    也没有对 **适销性** 或 **特定用途适用性** 的暗示保证。
    有关更多详细信息，请参阅 GNU 通用公共许可证。
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    您应该已经收到了 GNU 通用公共许可证的副本以及此程序。
    如果没有，请参阅 <https://www.gnu.org/licenses/>。
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
