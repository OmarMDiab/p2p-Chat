class PortAssigner:
    num_users=100
    user_ports = [[i, 0] for i in range(4001, 4000 + num_users)]

    @staticmethod
    def assign():
            for i in range(len(PortAssigner.user_ports)):
                port, flag = PortAssigner.user_ports[i]
                if flag == 0:
                    PortAssigner.user_ports[i][1] = 1
                    return port

            return -404
    
    
    @staticmethod
    def en_port(myport):
         for i in range(len(PortAssigner.user_ports)):
                port, flag = PortAssigner.user_ports[i]
                if port == myport:
                    PortAssigner.user_ports[i][1] = 0

         
         
         

