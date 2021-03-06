import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pickle
import cv2
from os.path import isfile
from builtins import str
from os import remove
from PIL import Image


# Classes originais do CIFAR-10
LABEL_NAMES = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

# Classes do projeto
ALTER_LABEL = ['Animal', 'Nao_Animal']


# Lê as imagens de um determinado batch e faz algumas conversões para que
# sua manipulação seja mais simples. Para mais informações sobre a base de dados leia o arquivo README.md
def load_batch(batch_id):
    # carrega o conteúdo do arquivo na variável batch
    with open("data_batch_" + str(batch_id), mode='rb') as file:
        batch = pickle.load(file, encoding='latin1')
    # carrega as imagens em si no array features
    features = batch['data'].reshape((len(batch['data']), 3, 32, 32)).transpose(0, 2, 3, 1)
    # carrega as classes das respectivas imagens no array labels
    labels = batch['labels']
    return features, labels


# Abre uma imagem a partir de um batch escolhido.
# recebe o batch a que a imagem pertence e o número desta imagem.
def show_image_from_batch(batch_id, num_img):
    if 0 <= num_img < 10000 and 1 <= batch_id < 6:
        features, labels = load_batch(batch_id)
        plt.axis('off')
        plt.imshow(features[num_img])
        plt.show()
        print("Classe Original: "+LABEL_NAMES[labels[num_img]])
        del features, labels # free memory


# Converte as imagens para o formato .png e as salva no diretorio deste arquivo.
# Recebe o batch ao qual elas pertencem e o intervalo de imagens a serem salvas.
def save_images(batch_id, indexInicio, indexFim):
    if 1 <= batch_id < 6:   # if necessário, pois só existem batchs do 1 ao 5
        if 0 <= indexInicio < indexFim <= 10000: # garante que a quantidade de imagens está dentro do intervalo possível
            features, labels = load_batch(batch_id)
            for id in range(int(indexInicio), int(indexFim)):
                path = "batch" + str(batch_id) + "-img" + str(id) + ".png"
                img = Image.fromarray(features[id], 'RGB')
                img.save(path)
            del features, labels


# Exclui as imagens no formato .png já salvas do projeto.
# Recebe o batch ao qual elas pertencem e o intervalo de imagens a serem deletadas.
def delete_images(batch_id, indexInicio, indexFim):
    if 1 <= batch_id < 6:   # if necessário, pois só existem batchs do 1 ao 5
        if 0 <= indexInicio < indexFim <= 10000: # garante que a quantidade de imagens está dentro do intervalo possível
            for id in range(int(indexInicio), int(indexFim)):
                path = "batch" + str(batch_id) + "-img" + str(id) + ".png"
                remove(path)

# imprime o histograma de uma imagem da base de dados
# recebe a base de dados a qual pertence a imagem
# o número de imagem
# obtive este código em:
# http://helloraspberrypi.blogspot.com/2015/10/python-opencv-generate-histograms-of.html
def plot_histogram(batch_id, numero_imagem):
    if 0 <= numero_imagem < 10000 and 1 <= batch_id < 6:
        save_images(batch_id, numero_imagem, numero_imagem + 1)
        img = Image.open("batch" + str(batch_id) + "-img" + str(numero_imagem) + ".png")
        imgArr = np.asarray(img)
        plt.subplot(221), plt.imshow(img)
        color = ('r', 'g', 'b')
        for i, col in enumerate(color):
            histr = cv2.calcHist([imgArr], [i], None, [256], [0, 256])
            plt.subplot(222), plt.plot(histr, color=col)
            plt.xlim([0, 256])

        plt.xlim([0, 256])
        plt.show()
        delete_images(batch_id, numero_imagem, numero_imagem + 1)


# utiliza a biblioteca OpenCV para converter imagens no formato .png
# para o formato grayscale (Preto e Branco). Recebe o diretório da imagem
def convert_to_grayscale(imagem_arquivo):
    if isfile(imagem_arquivo):
        image_rgb = cv2.imread(imagem_arquivo)
        image_gray = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2GRAY)
        return image_gray

# imprime uma imagem em grayscale
# recebe o batch da imagem
# e o número da imagem
def show_grayscale_image(batch_id, numero_imagem):
    if 0 <= numero_imagem < 10000 and 1 <= batch_id < 6:
        path = "batch" + str(batch_id) + "-img" + str(numero_imagem) + ".png"
        save_images(batch_id, numero_imagem, numero_imagem+1)
        file = Image.open(path)
        zoom_file = file.resize((250, 250))
        zoom_file.save(path)
        gray = convert_to_grayscale(path)
        cv2.imshow('Gray image', gray)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        delete_images(batch_id, numero_imagem, numero_imagem+1)


# Neste projeto subdividimos as 10 classes do cifar-10 em apenas duas (Animal e Nao_Animal)
# esta função converte o vetor, que possui as classes de cada imagem de um label e as converte
# nessas duas classes do projeto. O vetor de entrada pode ser obtido a partir da função load_batch
def alterar_labels(labels):
    alter_labels = []
    for l in labels:
        if 2 <= l <= 7: # é animal
            alter_labels.append(0)
        else: # não animal
            alter_labels.append(1)
    return alter_labels


# formata o arquivo .arff para ser testado no WEKA
# salva e converte as imagens para grayscale, em seguida as deleta
# recebe o nome do arquivo a ser formatado, o batch a ser formatado e o número de imagens (de 1 a 10000)
def format_arff_file_grayscale(arquivo_arff, batch_id, numero_imagens):
    if 0 <= numero_imagens <= 10000 and 1 <= batch_id < 6:
        features, labels = load_batch(batch_id)

        alter_label = alterar_labels(labels)
        save_images(batch_id, 0, numero_imagens)
        file = open(arquivo_arff, "w")

        # escrevendo comantários e itens iniciais do arquivo .arff
        file.writelines("% 1. Title: Database de objetos\n"
                        "%\n"
                        "% 2. Sources\n"
                        "%      Cifar-10 Database\n"
                        "%\n"
                        "@relation imagens\n\n")

        # escrevendo os atributos referentes ao vetor de características
        for num in range(0, 1024):
            file.writelines("@attribute 'valueof" + str(num) + "' real\n")
        file.writelines("@attribute 'class' {Animal, Nao_Animal}\n\n@data\n")

        # formata os pixels de cada imagem para ser escrito no arquivo
        for num in range(0, numero_imagens):
            path = "batch" + str(batch_id) + "-img" + str(num) + ".png"
            if isfile(path):  # checo se o arquivo existe
                aux = convert_to_grayscale(path)  # converto o arquivo atual para grayscale
                for i in range(0, 32):
                    for j in range(0, 32):
                        file.writelines(str(aux[i][j]) + ",")
                file.writelines(str(ALTER_LABEL[alter_label[num]]) + "\n")
        file.close()
        # desaloca os arrays, pois são muito grandes
        delete_images(batch_id, 0, numero_imagens)
        del features, labels, alter_label


# formata o arquivo .arff para ser testado no WEKA
# salva e converte as imagens para grayscale, em seguida as deleta
# recebe o nome do arquivo a ser formatado, o batch a ser formatado e o número de imagens (de 1 a 10000)
def format_arff_file_rgb(arquivo_arff, batch_id, numero_imagens):
    if 0 <= numero_imagens <= 10000 and 1 <= batch_id < 6:
        features, labels = load_batch(batch_id)

        alter_label = alterar_labels(labels)
        file = open(arquivo_arff, "w")

        # escrevendo comantários e itens iniciais do arquivo .arff
        file.writelines("% 1. Title: Database de objetos\n"
                        "%\n"
                        "% 2. Sources\n"
                        "%      Cifar-10 Database\n"
                        "%\n"
                        "@relation imagens\n\n")

        # escrevendo os atributos referentes ao vetor de características
        for num in range(0, 3072):
            file.writelines("@attribute 'valueof" + str(num) + "' real\n")
        file.writelines("@attribute 'class' {Animal, Nao_Animal}\n\n@data\n")

        # formata os pixels de cada imagem para ser escrito no arquivo
        for num in range(0, numero_imagens):
            for b in range(0, 32):
                for c in range(0, 32):
                    for d in range(0, 3):
                        file.writelines(str(features[num][b][c][d]) + ",")
            file.writelines(str(ALTER_LABEL[alter_label[num]]) + "\n")

        file.close()
        del features, labels, alter_label


# formata o arquivo .arff para ser testado no WEKA
# salva e converte as imagens para grayscale, em seguida as deleta
# recebe o nome do arquivo a ser formatado, o batch a ser formatado e o número de imagens (de 1 a 10000)
def format_arff_file_histogram(arquivo_arff, batch_id, numero_imagens):
    if 0 <= numero_imagens <= 10000 and 1 <= batch_id < 6:
        features, labels = load_batch(batch_id)

        alter_label = alterar_labels(labels)
        file = open(arquivo_arff, "w")

        # escrevendo comantários e itens iniciais do arquivo .arff
        file.writelines("% 1. Title: Database de objetos\n"
                        "%\n"
                        "% 2. Sources\n"
                        "%      Cifar-10 Database\n"
                        "%\n"
                        "@relation imagens\n\n")

        # escrevendo os atributos referentes ao vetor de características
        for num in range(0, 256):
            file.writelines("@attribute 'valueof" + str(num) + "' real\n")
        file.writelines("@attribute 'class' {Animal, Nao_Animal}\n\n@data\n")

        color = ('r', 'g', 'b')
        # formata os pixels de cada imagem para ser escrito no arquivo
        for num in range(0, numero_imagens):
            histr = []
            for i, col in enumerate(color):
                histr = cv2.calcHist([features[num]], [i], None, [256], [0, 256])
            for j in histr:
                file.writelines(str(int(j[0])) + ",")
            file.writelines(str(ALTER_LABEL[alter_label[num]]) + "\n")

        file.close()
        del features, labels, alter_label


# formata um batch (1 a 5) para ser treinado pela rede neural
# salva e converte as imagens para grayscale, em seguida as deleta
# deixa o vetor de caracteristicas de saída no formato unidimensional
# recebe o batch a ser formatado e o intervalo de imagens a ser formatadas (valor entre 1 e 10000)
def format_batch_train_grayscale(batch_id, indexInicio, indexFim):
    if 0 <= indexInicio < indexFim <= 10000 and 1 <= batch_id < 6:
        save_images(batch_id, indexInicio, indexFim)
        features, labels = load_batch(batch_id)

        array_labels = alterar_labels(labels)  # array com os labels animal ou nao_animal
        array_features = []  # array das imagens em preto em branco

        for num in range(int(indexInicio), int(indexFim)):
            array_aux = []
            path = "batch" + str(batch_id) + "-img" + str(num) + ".png"
            img_gray = convert_to_grayscale(path)  # converto o arquivo atual para grayscale

            # a imagem está no formato matricial grayscale 32x32
            # a convertemos para uma array unidimensional de 1024 posições
            for i in range(0, 32):
                for j in range(0, 32):
                    array_aux.append(img_gray[i][j])
            array_features.append(array_aux)

        delete_images(batch_id, indexInicio, indexFim)
        del features, labels
        return array_features, array_labels


# formata um batch (1 a 5) para ser treinado pela rede neural
# utiliza as imagens em rgb direto da base de dados. Não precisa converter para .png
# deixa o vetor de caracteristicas de saída no formato unidimensional
# recebe o batch a ser formatado e o intervalo de imagens a ser formatadas (valor entre 1 e 10000)
def format_batch_train_rgb(batch_id, indexInicio, indexFim):
    if 0 <= indexInicio < indexFim <= 10000 and 1 <= batch_id < 6:
        features, labels = load_batch(batch_id)
        array_labels = alterar_labels(labels)
        array_features = []
        for a in range(int(indexInicio), int(indexFim)):
            array = []
            for b in range(0, 32):
                for c in range(0, 32):
                    for d in range(0, 3):
                        array.append(features[a][b][c][d])
            array_features.append(array)

        del features, labels
        return array_features, array_labels


# formata um batch (1 a 5) para ser treinado pela rede neural
# utiliza as imagens em rgb direto da base de dados. Não precisa converter para .png
# deixa o vetor de caracteristicas de saída no formato unidimensional
# recebe o batch a ser formatado e o intervalo de imagens a ser formatadas (valor entre 1 e 10000)
def format_batch_train_histogram(batch_id, indexInicio, indexFim):
    if 0 <= indexInicio < indexFim <= 10000 and 1 <= batch_id < 6:
        features, labels = load_batch(batch_id)
        array_labels = alterar_labels(labels)
        array_features = []
        color = ('r', 'g', 'b')
        for a in range(int(indexInicio), int(indexFim)):
            array = []
            histr = []
            for i, col in enumerate(color):
                histr = cv2.calcHist([features[a]], [i], None, [256], [0, 256])
            for j in histr:
                array.append(j[0])
            array_features.append(array)

        del features, labels
        return array_features, array_labels


if __name__ == '__main__':
    COUNT_IMG = 50
    #format_arff_file_histogram(arquivo_arff="hist-batch" + str(i) + ".arff", batch_id=i, numero_imagens=COUNT_IMG)
    #show_grayscale_image(1,0)
    #show_image_from_batch(1,0)
    #plot_histogram(1,0)
    '''
    for i in range(1, 6):
        format_arff_file_rgb(arquivo_arff="rgb-batch" + str(i) + ".arff", batch_id=i, numero_imagens=COUNT_IMG)
        format_arff_file_grayscale(arquivo_arff="gray-batch" + str(i) + ".arff", batch_id=i, numero_imagens=COUNT_IMG)
        format_arff_file_histogram(arquivo_arff="hist-batch" + str(i) + ".arff", batch_id=i, numero_imagens=COUNT_IMG)
    '''
    save_images(1,0,1)
    x = convert_to_grayscale("batch1-img0.png")