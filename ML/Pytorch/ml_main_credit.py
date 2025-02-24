import pdb
from client import Client
from softmax_model import SoftmaxModel
from mnist_cnn_model import MNISTCNNModel
from lfw_cnn_model import LFWCNNModel
from svm_model import SVMModel
import datasets

def returnModel(D_in, D_out):
    model = SoftmaxModel(D_in, D_out)
    # model = MNISTCNNModel()
    return model

# Initialize Clients
# First Client is the aggregator
def centralize_test():
    clients = []
    dataset = "creditcard"
    D_in = datasets.get_num_features(dataset)
    D_out = datasets.get_num_classes(dataset)
    batch_size = 4
    train_cut = 0.8
    
    model = returnModel(D_in, D_out)    
    my_client = Client(dataset, dataset + "train", batch_size, model, train_cut)

    model = returnModel(D_in, D_out)
    test_client = Client(dataset, dataset+"test", batch_size, model, 0)

    modelWeights = my_client.getModelWeights()

    for iter in range(1001):
        
        # Calculate and aggregaate gradients    
        grad = my_client.getGrad()
        
        # Share updated model
        modelWeights = modelWeights - grad
        my_client.updateModel(modelWeights)

        # modelWeights = my_client.getModelWeights()
        # for i in range(1):
        #     clients[i].updateModel(modelWeights)
        
        # Print average loss across clients
        if iter % 100 == 0:
            loss = my_client.getLoss()
            print("Average loss is " + str(loss))

            test_client.updateModel(modelWeights)
            test_err = test_client.getTestErr()
            print("Test error: " + str(test_err) + "\n")

    pdb.set_trace()


def main():
    clients = []
    dataset = "creditcard"
    D_in = datasets.get_num_features(dataset)
    D_out = datasets.get_num_classes(dataset)
    batch_size = 4
    train_cut = 0.8

    for i in range(10):
        model = returnModel(D_in, D_out)    
        clients.append(Client(dataset, dataset + "train", batch_size, model, train_cut))

    model = returnModel(D_in, D_out)
    test_client = Client(dataset, dataset+"test", batch_size, model, 0)

    for iter in range(1000):
        # Calculate and aggregaate gradients    
        for i in range(10):
            clients[0].updateGrad(clients[i].getGrad())
        
        # Share updated model
        clients[0].step()
        modelWeights = clients[0].getModelWeights()
        for i in range(10):
            clients[i].updateModel(modelWeights)
        
        # Print average loss across clients
        if iter % 100 == 0:
            loss = 0.0
            for i in range(10):
                loss += clients[i].getLoss()
            print("Average loss is " + str(loss / len(clients)))

            test_client.updateModel(modelWeights)
            test_err = test_client.getTestErr()
            print("Test error: " + str(test_err) + "\n")

    test_client.updateModel(modelWeights)
    test_err = test_client.getTestErr()
    pdb.set_trace()

if __name__ == "__main__":
    centralize_test()