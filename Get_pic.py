import gen_pic
import getComment

if __name__ == '__main__':
    music_id = input("music_id:")
    music_name = input("music_name:")
    comment_number = input("comment_number:")
    # id:R_SO_4_254574 name:后来 comment_number:2000
    getComment.getCSV(music_id, comment_number, music_name)
    gen_pic.gen_pic(music_name)

