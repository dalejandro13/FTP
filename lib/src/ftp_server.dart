
import 'dart:async';
import 'dart:io';

import 'package:tcp_server/src/ftp_client.dart';

class FtpServer{
  String _ipAddress;
  int _port;
  ServerSocket _serverSocket;
  List<FtpClient> clients = [];

  // FtpServer(){
  //   _ipAddress = '10.0.2.15';
  //   _port = 21;

  //   start();
  // }

  FtpServer.createServer(ipAddress, port){
    this._ipAddress = ipAddress;
    this._port = port;

    start();
  }

  start() async {
    try{
      Future<ServerSocket> serverFuture = ServerSocket.bind(_ipAddress, _port);
      serverFuture.then((ServerSocket server) {
      _serverSocket = server;
      print("Created Server Socket");
      server.listen((Socket socket) async {
        await Future.delayed(Duration(seconds: 1));
        clients.add(FtpClient(socket));
        /*socket.writeln("Flutter FTP Server");
        socket.flush();*/
      });
    });
    }
    catch(e){
      print(e);
    }
  }

  stop(){
    if(_serverSocket != null){
      _serverSocket.close();
    }
  }

  /*_serverListener(Socket socket){
    _socket = socket;
    _socket.listen((List<int> data) => _dataReceiver(data));

  }*/
  


}