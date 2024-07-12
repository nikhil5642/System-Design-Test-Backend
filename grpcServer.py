from concurrent import futures
import os
import time
import grpc
import myFirstGrpc_pb2
import myFirstGrpc_pb2_grpc

# Use HTTP 2.0
class Greeter(myFirstGrpc_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):
        return myFirstGrpc_pb2.HelloReply(message='Hello, {}!'.format(request.name))
    
    def StreamGreetings(self, request, context):
        for i in range(10):
            yield myFirstGrpc_pb2.HelloReply(message='Hello %s %d' % (request.name, i))
            time.sleep(1)

    def SendGreetings(self, request_iterator, context):
        names = []
        for request in request_iterator:
            names.append(request.name)
        return myFirstGrpc_pb2.HelloReply(message='Hello %s' % ' '.join(names))

    def Chat(self, request_iterator, context):
        for request in request_iterator:
            yield myFirstGrpc_pb2.HelloReply(message='Hello %s' % request.name)

    def DownloadFile(self, request, context):
        filename = request.filename
        if not os.path.exists(filename):
            context.set_details(f'File not found: {filename}')
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return

        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(1024 * 64)  # Read in 64kB chunks
                if not chunk:
                    break
                yield myFirstGrpc_pb2.FileChunk(content=chunk)
                
def serveGRPC():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    myFirstGrpc_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('0.0.0.0:50051')
    server.start()
    server.wait_for_termination()

