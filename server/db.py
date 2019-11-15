import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")

database = client["crowd_mei"]
file_col = database["files"]
page_col = database["pages"]

# # File and page data examples
# file_col.insert_one({"file_path": "data/pdf/grades.pdf",
#                      "no_pages": 10})


# page_col.insert_many([
#     {"file_id": 1, "page_id": 1, "png_path": "",
#      "jpg_path": "data/pdf/IMSLP109835-PMLP30951-sibley.1802.1525.beethoven.andante.fmajor.jpg",
#      "mei_path": "", "is_checked": False},
#     {"file_id": 1, "page_id": 2, "png_path": "",
#      "jpg_path": "data/pdf/IMSLP109835-PMLP30951-sibley.1802.1525.beethoven.andante.fmajor.jpg",
#      "mei_path": "", "is_checked": False}])




