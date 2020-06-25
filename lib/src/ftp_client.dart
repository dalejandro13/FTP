import 'dart:io';
//import 'package:path_provider/path_provider.dart';

class FtpClient{
  Socket _socket;
  String _address;
  String _password;
  int _port;
  String _username;
  String _pathForFiles;
  String _transferType;

  FtpClient(Socket socket){
    _socket = socket;
    _address = _socket.remoteAddress.address;
    _port = _socket.remotePort;

    _socket.writeln("220 Ready!");
    try{
      _socket.listen((List<int> data) => _dataReceiver(data));
    }
    catch(e){
      print(e);
    }
  }

  _dataReceiver(List<int> data){
    String response = null;
    String result = new String.fromCharCodes(data);
    List<String> command = result.split(' ');

    String cmd = command[0].toUpperCase();
    String arguments = command.length > 1 ? result.substring(command[0].length + 1)  : null; 

    if(arguments == null || arguments.isEmpty)
      arguments = null;

    print('Command: ' + command.toString());
    
    if(response == null){
      switch(cmd.trim()){
        case "USER":
          response = _setUsername(arguments);
          break;
        case "PASS":
          response = _setPassword(arguments);
          break;
        case "CWD":
          response = _changeWorkingDirectory(arguments);
          break;
        case "CDUP":
          response = _updateWorkingDirectory(arguments);
          break;
        case "PWD":
          response = _getWorkingDirectory();
          break;
        case "QUIT":
          response = '221 Service closing control connection';
          break;
        case "TYPE":
          List<String> splitArgs = arguments.split(' ');
          response = _type(splitArgs[0], splitArgs.length > 1 ? splitArgs[1] : null);
          break;
        case "PASV":
          response = "227 Entering Passive Mode (10, 0, 2, 15, 30, 1)"; //(10, 0, 2, 15, 30, 00)"; //(63, 247, 72, 82, 238, 5)";
          break;
        case "PORT":
          //String val = command[1].trim();
          //String val2 = _putSpace(command[1]);
          response = "200 Command PORT okay 10, 0, 2, 15, 1, 1"; //"200 Port command successful"; /*"200 PORT ${val2}";*/ //"200 PORT 10, 0, 2, 15, 1, 1"; //"200 PORT 10, 0, 2, 15, 30, 04";  //"200 PORT 10, 0, 2, 15, 63, 1"; //puerto y direccion IP que envia el cliente hacia el servidor para establecer la comunicacion //formula (p1*256) + p2
          break;
        case 'LIST':
          response = "551 File listing failed"; /*"200 OK";*/ /*"150 Opening BINARY mode data connection.";*/ /*"150 File status okay; about to open data connection";*/ //"150 Opening ASCII mode data connection for file list";
          break;
        default:
          print("502 $cmd");
          response = "502 Command not implemented.";
          break;
      }
    }
    _socket.writeln(response);
    _socket.flush();
  }

  String _putSpace(String command){
    String acum = '';
    for(int i = 0; i < command.length; i++){
      acum += command[i];
      if(command[i] == ','){
        acum += ' ';
      }
    }
    return acum;
  }

  String _setUsername(String username){
    _username = username.trim();
    if(_username == "flexo"){
      return "331 user ok, need password";
    }
    else{
      return "430 invalid password";
    }
  }

  String _setPassword(String password){
    _password = password.trim();
    if(_password == "1234"){
      return "230 User logged in";
    }else{
      return "530 Not logged in";
    }
  }

  String _getWorkingDirectory(){
    return("257 /home/flexo/Documents is the current location");
  }

  String _changeWorkingDirectory(String pathname){
    return("250 Directory changed to \"/\"");

    // if(response == "230"){
    //   if(pathname != " "){
    //     _pathForFiles = '/home/flexo/Documents/';
    //     return "250 Changed to new directory";
    //   }
    // }    
  }

  String _updateWorkingDirectory(String path){
    return("200 CDUP sucessful. / is current directory.");
  }

  String _type(String typeCode, String formatControl)
  {
    String response = "";

    switch (typeCode.trim())
    {
        case "A":
        case "I":
          _transferType = typeCode;
          response = "200 OK";
          break;
        case "E":
        case "L":
        default:
            response = "504 Command not implemented for that parameter.";
            break;
    }

    if (formatControl != null)
    {
        switch (formatControl)
        {
            case "N":
                response = "200 OK";
                break;
            case "T":
            case "C":
            default:
                response = "504 Command not implemented for that parameter.";
                break;
        }
    }

    return response;
  }

}