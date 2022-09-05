#YOLOv5 🚀 de Ultralytics, licencia GPL-3.0
"""
Run YOLOv5 detection inference on images, videos, directories, globs, YouTube, webcam, streams, etc.

Usage - sources:
    $ python detect.py --weights yolov5s.pt --source 0                               # webcam
                                                     img.jpg                         # image
                                                     vid.mp4                         # video
                                                     path/                           # directory
                                                     'path/*.jpg'                    # glob
                                                     'https://youtu.be/Zgi9g1ksQHc'  # YouTube
                                                     'rtsp://example.com/media.mp4'  # RTSP, RTMP, HTTP stream

Usage - formats:
    $ python detect.py --weights yolov5s.pt                 # PyTorch
                                 yolov5s.torchscript        # TorchScript
                                 yolov5s.onnx               # ONNX Runtime or OpenCV DNN with --dnn
                                 yolov5s.xml                # OpenVINO
                                 yolov5s.engine             # TensorRT
                                 yolov5s.mlmodel            # CoreML (macOS-only)
                                 yolov5s_saved_model        # TensorFlow SavedModel
                                 yolov5s.pb                 # TensorFlow GraphDef
                                 yolov5s.tflite             # TensorFlow Lite
                                 yolov5s_edgetpu.tflite     # TensorFlow Edge TPU
"""

import argparse
import os
import platform
import sys
from pathlib import Path

import torch

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  #Directorio raíz YOLOv5
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  #agregar ROOT a PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  #Pariente

from models.common import DetectMultiBackend
from utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from utils.general import (LOGGER, Profile, check_file, check_img_size, check_imshow, check_requirements, colorstr, cv2,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, smart_inference_mode


@smart_inference_mode()
def run(
        weights=ROOT / 'yolov5s.pt',  #model.pt ruta(s)
        source=ROOT / 'data/images',  #file/dir/URL/glob, 0 para webcam
        data=ROOT / 'data/coco128.yaml',  #Ruta de acceso dataset.yaml
        imgsz=(640, 640),  #tamaño de inferencia (altura, anchura)
        conf_thres=0.25,  #umbral de confianza
        iou_thres=0.45,  #Umbral de pagaré NMS
        max_det=1000,  #detecciones máximas por imagen
        device='',  #dispositivo cuda, es decir, 0 o 0,1,2,3 o cpu
        view_img=False,  #mostrar resultados
        save_txt=False,  #Guardar los resultados en *.txt
        save_conf=False,  #Guardar confianzas en etiquetas --save-txt
        save_crop=False,  #Guardar cuadros de predicción recortados
        nosave=False,  #no guarde imágenes/vídeos
        classes=None,  #filtrar por clase: --clase 0 o --clase 0 2 3
        agnostic_nms=False,  #NMS agnóstico de clase
        augment=False,  #inferencia aumentada
        visualize=False,  #visualizar características
        update=False,  #actualizar todos los modelos
        project=ROOT / 'runs/detect',  #Guardar los resultados en proyecto/nombre
        name='exp',  #Guardar los resultados en proyecto/nombre
        exist_ok=False,  #Proyecto/nombre existente ok, no incrementar
        line_thickness=3,  #grosor del cuadro delimitador (píxeles)
        hide_labels=False,  #ocultar etiquetas
        hide_conf=False,  #ocultar confidencias
        half=False,  #utilizar la inferencia de media precisión FP16
        dnn=False,  #Utilice OpenCV DNN para la inferencia ONNX
):
    source = str(source)
    save_img = not nosave and not source.endswith('.txt')  #guardar imágenes de inferencia
    is_file = Path(source).suffix[1:] in (IMG_FORMATS + VID_FORMATS)
    is_url = source.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
    webcam = source.isnumeric() or source.endswith('.txt') or (is_url and not is_file)
    if is_url and is_file:
        source = check_file(source)  #descargar
#Directorios
    save_dir = increment_path(Path(project) / name, exist_ok=exist_ok)  #ejecución de incremento
    (save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  #hacer dir
#Modelo de carga
    device = select_device(device)
    model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data, fp16=half)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = check_img_size(imgsz, s=stride)  #comprobar el tamaño de la imagen
#Cargador de datos
    if webcam:
        view_img = check_imshow()
        dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt)
        bs = len(dataset)  #Tamaño del lote
    else:
        dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)
        bs = 1  #Tamaño del lote
    vid_path, vid_writer = [None] * bs, [None] * bs

    #Ejecutar inferencia
    model.warmup(imgsz=(1 if pt else bs, 3, *imgsz))  #Calentamiento
    seen, windows, dt = 0, [], (Profile(), Profile(), Profile())
    for path, im, im0s, vid_cap, s in dataset:
        with dt[0]:
            im = torch.from_numpy(im).to(device)
            im = im.half() if model.fp16 else im.float()  #uint8 a fp16/32
            im /= 255  #0 - 255 a 0.0 - 1.0
            if len(im.shape) == 3:
                im = im[None]  #expandir para la atenuación por lotes
#Inferencia
        with dt[1]:
            visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False
            pred = model(im, augment=augment, visualize=visualize)

        #Nms
        with dt[2]:
            pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)

        #Clasificador de segunda etapa (opcional)
#pred = utils.general.apply_classifier(pred, classifier_model, im, im0s)
#Predicciones de procesos
        for i, det in enumerate(pred):  #por imagen
            seen += 1
            if webcam:  #batch_size >= 1
                p, im0, frame = path[i], im0s[i].copy(), dataset.count
                s += f'{i}: '
            else:
                p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)

            p = Path(p)  #a ruta
            save_path = str(save_dir / p.name)  #Im.jpg
            txt_path = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  #Im.txt
            s += '%gx%g ' % im.shape[2:]  #cadena de impresión
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  #ganancia de normalización whwh
            imc = im0.copy() if save_crop else im0  #para save_crop
            annotator = Annotator(im0, line_width=line_thickness, example=str(names))
            if len(det):
                #Reescalar cajas de tamaño img_size a im0
                det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()

                #Imprimir resultados
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  #detecciones por clase
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  #agregar a cadena
#Escribir resultados
                for *xyxy, conf, cls in reversed(det):
                    if save_txt:  #Escribir en archivo
                        xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  #xywh normalizado
                        line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  #formato de etiqueta
                        with open(f'{txt_path}.txt', 'a') as f:
                            f.write(('%g ' * len(line)).rstrip() % line + '\n')

                    if save_img or save_crop or view_img:  #Agregar bbox a la imagen
                        c = int(cls)  #clase integer
                        label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                        annotator.box_label(xyxy, label, color=colors(c, True))
                    if save_crop:
                        save_one_box(xyxy, imc, file=save_dir / 'crops' / names[c] / f'{p.stem}.jpg', BGR=True)

            #Resultados de la transmisión
            im0 = annotator.result()
            if view_img:
                if platform.system() == 'Linux' and p not in windows:
                    windows.append(p)
                    cv2.namedWindow(str(p), cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)  #Permitir el cambio de tamaño de la ventana (Linux)
                    cv2.resizeWindow(str(p), im0.shape[1], im0.shape[0])
                cv2.imshow(str(p), im0)
                cv2.waitKey(1)  #1 milisegundo
#Guardar resultados (imagen con detecciones)
            if save_img:
                if dataset.mode == 'image':
                    cv2.imwrite(save_path, im0)
                else:  #'video' o 'stream'
                    if vid_path[i] != save_path:  #nuevo video
                        vid_path[i] = save_path
                        if isinstance(vid_writer[i], cv2.VideoWriter):
                            vid_writer[i].release()  #lanzar escritor de video anterior
                        if vid_cap:  #Vídeo
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        else:  #Corriente
                            fps, w, h = 30, im0.shape[1], im0.shape[0]
                        save_path = str(Path(save_path).with_suffix('.mp4'))  #forzar *.mp4 sufijo en los vídeos de resultados
                        vid_writer[i] = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                    vid_writer[i].write(im0)

        #Tiempo de impresión (solo inferencia)
        LOGGER.info(f"{s}{'' if len(det) else '(no detections), '}{dt[1].dt * 1E3:.1f}ms")

    #Imprimir resultados
    t = tuple(x.t / seen * 1E3 for x in dt)  #velocidades por imagen
    LOGGER.info(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS per image at shape {(1, 3, *imgsz)}' % t)
    if save_txt or save_img:
        s = f"\n{len(list(save_dir.glob('labels/*.txt')))} labels saved to {save_dir / 'labels'}" if save_txt else ''
        LOGGER.info(f"Results saved to {colorstr('bold', save_dir)}{s}")
    if update:
        strip_optimizer(weights[0])  #actualizar el modelo (para corregir SourceChangeWarning)


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default=ROOT / 'yolov5s.pt', help='model path(s)')
    parser.add_argument('--source', type=str, default=ROOT / 'data/images', help='file/dir/URL/glob, 0 for webcam')
    parser.add_argument('--data', type=str, default=ROOT / 'data/coco128.yaml', help='(optional) dataset.yaml path')
    parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=[640], help='inference size h,w')
    parser.add_argument('--conf-thres', type=float, default=0.25, help='confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
    parser.add_argument('--max-det', type=int, default=1000, help='maximum detections per image')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='show results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
    parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --classes 0, or --classes 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--visualize', action='store_true', help='visualize features')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--project', default=ROOT / 'runs/detect', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
    parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
    parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
    parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
    parser.add_argument('--dnn', action='store_true', help='use OpenCV DNN for ONNX inference')
    opt = parser.parse_args()
    opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  #Expandir
    print_args(vars(opt))
    return opt


def main(opt):
    check_requirements(exclude=('tensorboard', 'thop'))
    run(**vars(opt))


if __name__ == "__main__":
    opt = parse_opt()
    main(opt)
