unzip ./instantclient-basic-linux.x64-12.1.0.2.0.zip -d /opt/oracle
unzip ./instantclient-sdk-linux.x64-12.1.0.2.0.zip -d /opt/oracle
ln -sfn /opt/oracle/instantclient_12_1 /opt/oracle/instantclient
ln -s /opt/oracle/instantclient/libclntsh.so.12.1 /opt/oracle/instantclient/libclntsh.so
ln -s /opt/oracle/instantclient/libocci.so.12.1 /opt/oracle/instantclient/libocci.so
