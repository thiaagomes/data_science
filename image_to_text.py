import oci
import os
import base64
import ocifs
import PIL.Image as Image
import io
import re

#Inicialização dos clients
config = oci.config.from_file('config')
ai_vision_client = oci.ai_vision.AIServiceVisionClient(config=config)
fs = ocifs.OCIFileSystem()
object_storage_client = oci.object_storage.ObjectStorageClient(config)

#Lendo as imagens do bucket. Esta função fs.glob possui a seguinte sintaxe:
#"oci://<bucket_name>@<namespace>/arquivos"

img_list = fs.glob("oci://bucket-demo@idi1o0a010nx*.jpg")

name_list = []
for i, item in enumerate(img_list):
    name = item.rsplit('/', 1)[1]
    name_list.append(name)
    
code_list = []
for i in range(0, len(txt_list)):
    codigo = txt_list[i]
    s = [float(s) for s in re.findall(r'-?\d+\.?\d*', codigo)]
    code_list.append(int(s[1]))

for i, file in enumerate(img_list):
        with fs.open(file) as f:
            content = f.read()
            
            encoded_string = base64.b64encode(content, altchars=None)
            decoded_string = encoded_string.decode("utf-8", "ignore")

                
            #Não estranhar o idioma marcado como inglês, a ferramenta também lida com textos em pt-br, mas há um hardblock interno
            #que bloqueia a extração de texto se o idioma detctado for não-inglês, então travamos ele na chamada da API.
            
            analyze_document_response = ai_vision_client.analyze_document(
                    analyze_document_details=oci.ai_vision.models.AnalyzeDocumentDetails(
                    compartment_id = "ocid1.compartment.oc1..aaaaaaaal63rmctoojg7q2pvdpeuqknebyaqg3h7gcci6whf74ht7tfapl4q",
                    features=[
                        oci.ai_vision.models.DocumentTextDetectionFeature(
                            feature_type="TEXT_DETECTION")],
                    language='ENG', #Sim, o idioma é ENG mesmo. A ferramenta tem um hardblock para textos não-inglês
                    document=oci.ai_vision.models.InlineDocumentDetails(
                    source="INLINE",
                    data=decoded_string)))

            #Extraimos as palavras da response da API e limpamos o texto, pois vem recheado de colchetes e aspas
            
            words = str([word.text for page in analyze_document_response.data.pages for word in page.words])
            name = f"{i}.txt" 
            
            words_str_1 = words.replace("',",'')
            words_str_2 = words_str_1.replace("'",'')
            words_str_3 = words_str_2.replace("[",'')
            words_str_4 = words_str_3.replace("]",'')

            #Colocamos o resultado no bucket correspondente que criamos para receber estes textos
            
            put_object_response = object_storage_client.put_object(
                namespace_name="idi1o0a010nx", #TO DO
                bucket_name="bucket-demo", #TO DO
                object_name=name,
                put_object_body = words_str_4,
                content_type="text/plain")
            
            print("Documento", name, "upado!")