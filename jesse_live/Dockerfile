FROM screoff/jesse:0.23.0

LABEL Maintainer="Sebastien Creoff"

WORKDIR /jesse_live
COPY ./ /jesse_live
RUN pip3 install Binance_Futures_Python
RUN pip3 install -e .

WORKDIR /home
