import os
import cv2
import json
import main_config as mc

# get all the image filnames
image_filenames = os.listdir(mc.images_path)


#### Split dataset to training, validation and testing ####
training_ds = round(len(image_filenames)*mc.training_split)
validation_ds = round(len(image_filenames)*mc.validation_split)
evaluation_ds = round(len(image_filenames)*mc.evaluation_split)

if training_ds+validation_ds+evaluation_ds > len(image_filenames):
    training_ds -= abs(training_ds+validation_ds+evaluation_ds - len(image_filenames))

training_filenames = image_filenames[:training_ds]
validation_filenames = image_filenames[training_ds:training_ds+validation_ds]
evaluation_filenames = image_filenames[training_ds+validation_ds:training_ds+validation_ds+evaluation_ds]

training_filenames = image_filenames[:training_ds]
validation_filenames = image_filenames[training_ds:training_ds+validation_ds]
evaluation_filenames = image_filenames[training_ds+validation_ds:training_ds+validation_ds+evaluation_ds]


# function for yolo format to coco
def yolo_to_coco(x_center, y_center, w, h,  image_w, image_h, class_name):
    w = w * image_w
    h = h * image_h
    x1 = ((2 * x_center * image_w) - w)/2
    y1 = ((2 * y_center * image_h) - h)/2
    return [x1, y1, w, h, class_name]

# iterate to all of the labels in a specific label text file
def iterate_labels(labels, image_w, image_h):
    labels_list = []
    for label in labels:
        if label == "":
            continue
        cl, x, y, w, h = [float(x) for x in label.split(" ")]
        label = yolo_to_coco(x, y, w, h, image_w, image_h, int(cl))
        labels_list.append(label)
    return labels_list

# main function to convert coco128 to coco json file that accepts by mmdet
def convert_to_coco():
    print("Creating json files for coco")
    # iterate through all of the filenames with their corresponding name where they will be saved
    for img_filenames, suff in zip([training_filenames, validation_filenames, evaluation_filenames], [mc.coco_train, mc.coco_val, mc.coco_val]):
        # initialize list
        categ_list = []
        image_list = []
        annot_list = []
        annot_id = 0
        image_id = 0

        # create dictionaries from class names
        for idx, c in enumerate(mc.class_names):
            cat_dict = {'id': idx, 'name': c}
            categ_list.append(cat_dict)

        # iterate over image files
        for image_filename in img_filenames:
            # split the file name and add .txt to get the corresponding label text file
            label_filename = image_filename.split(".")[0]+".txt"
            label_fpath = os.path.join(mc.labels_path, label_filename)
            image_fpath = os.path.join(mc.images_path, image_filename)

            # read image via cv2 to get the image height and width
            img = cv2.imread(image_fpath)
            image_h, image_w, image_c =  img.shape

            # create dictionary for image
            image_dict = {
                "id": image_id,
                "width": image_w,
                "height": image_h,
                "file_name": image_filename,
                }

            # open label text file and get all the annotations and classes for a certain image
            with open(label_fpath, 'r') as f:
                labels = f.read().split("\n")
                labels = iterate_labels(labels, image_w, image_h)

            # iterate over the labels/annotaions to create dictionaries
            for label in labels:
                data_anno = dict(image_id = image_id,
                                id = annot_id,
                                category_id = label[4],
                                bbox = label[:4],
                                area = label[2] * label[3],
                                segmentation = [],
                                iscrowd = 0)
                annot_list.append(data_anno)
                annot_id += 1

            image_id += 1
            image_list.append(image_dict)

        # sample cocoformat
        coco_format_json = dict(
            images=image_list,
            annotations=annot_list,
            categories=categ_list)

        with open(suff, "w") as outfile:
            json.dump(coco_format_json, outfile)

        print("Done converting dataset to coco json files")