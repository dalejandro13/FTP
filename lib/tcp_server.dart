library simple_ftp;

import 'package:tcp_server/src/ftp_server.dart';

/// A Calculator.
class SimpleFTP{
  FtpServer _ftpServer;

  SimpleFTP() {
    _ftpServer = FtpServer.createServer('10.0.2.15', 3000);
  }
}
