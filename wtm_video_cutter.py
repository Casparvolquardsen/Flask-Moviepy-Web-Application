from moviepy.editor import *
from moviepy.video.VideoClip import ImageClip
from moviepy.video.fx.resize import resize
import os


def reformat_string(plain_string: str, max_width: int, align_left=True):
    formatted = ""

    while len(plain_string) > 0:
        # string is too long and would be cut of the screen
        if len(plain_string) > max_width:
            temp_index = max_width - 1
            while temp_index > 0:
                if plain_string[temp_index] == " ":
                    appended_text = plain_string[:temp_index]
                    if align_left:
                        appended_text += (max_width - len(appended_text)) * " "
                    formatted += appended_text + "\n"
                    plain_string = plain_string[temp_index + 1:]
                    break
                else:
                    temp_index -= 1
            if temp_index == 0:
                formatted += plain_string[:max_width] + "\n"
                plain_string = plain_string[max_width:]
        # string length is fine
        else:
            if align_left:
                plain_string += (max_width - len(plain_string)) * " "
            formatted += plain_string
            plain_string = ""

    return formatted


def get_num_lines(input_str: str):
    if input_str == '':
        return 0
    else:
        return input_str.count("\n") + 1


def create_final_clip(short_title: str, long_title: str, authors: str, video_id: int, file_extension: str,
                      upload_dir: str, output_dir: str, sub_title="", additional_information="", acknowledgement=""):
    # Configuration
    INTRO_LENGTH = 5
    WIDTH, HEIGHT = SCREENSIZE = (1920, 1080)
    LEFT_PADDING = RIGHT_PADDING = 100
    UPPER_PADDING = 100
    BOTTOM_PADDING = 100
    TITLE_WIDTH = 32
    TITLE_FONT = "AgencyFB-Bold"
    TITLE_FONTSIZE = 115
    TITLE_FONTCOLOR = "rgb(255,230,0)"
    STANDARD_WIDTH = 75
    STANDARD_FONT = "Tahoma"
    STANDARD_FONTSIZE = 48
    STANDARD_FONTCOLOR = "rgb(255,255,255)"
    LINK_FONTCOLOR = "rgb(190,190,255)"
    PARAGRAPH_SPACING = 50
    LOGO_HEIGHT = 200
    SPEED = 200

    cwd = os.getcwd()

    # Directories
    SOURCES_DIR = f"{cwd}/static"

    # Text
    UHH_DESCRIPTION = "University of Hamburg    \n" \
                      "Department of Informatics\n" \
                      "Knowledge Technology     "
    INTRO_WEBSITE_LINK = "http://www.knowledge-technology.info"
    OUTRO_WEBSITE_LINK = "For more information please see     \n" \
                         "http://www.knowledge-technology.info"
    # Logos
    WTM_LOGO_PATH = f"{SOURCES_DIR}/logos/KT_Logo_Black_RGB_Cropped.png"
    UHH_LOGO_PATH = f"{SOURCES_DIR}/logos/UHH_Logo_Black_RGB.png"

    # Input
    short_title = short_title.upper()
    long_title = reformat_string(long_title.upper(), TITLE_WIDTH)
    sub_title = reformat_string(sub_title, STANDARD_WIDTH)
    authors = reformat_string(authors, STANDARD_WIDTH)
    additional_information = reformat_string(additional_information, STANDARD_WIDTH)
    acknowledgement = reformat_string(acknowledgement, STANDARD_WIDTH)

    # Positions
    # Intro
    long_title_posiiton = (LEFT_PADDING, UPPER_PADDING)
    sub_title_position = (
        LEFT_PADDING, long_title_posiiton[1] + get_num_lines(long_title) * TITLE_FONTSIZE + (
            PARAGRAPH_SPACING if get_num_lines(sub_title) > 0 else 0))
    authors_position = (
        LEFT_PADDING, sub_title_position[1] + get_num_lines(sub_title) * STANDARD_FONTSIZE + (
            PARAGRAPH_SPACING if get_num_lines(authors) > 0 else 0))
    # Relative to bottom
    link_position = (LEFT_PADDING, HEIGHT - BOTTOM_PADDING - get_num_lines(INTRO_WEBSITE_LINK) * STANDARD_FONTSIZE)
    uhh_position = (
        LEFT_PADDING, link_position[1] - PARAGRAPH_SPACING - get_num_lines(UHH_DESCRIPTION) * STANDARD_FONTSIZE)
    # Logo positions
    uhh_logo_position = (round(WIDTH - RIGHT_PADDING - LOGO_HEIGHT * 2.156863), HEIGHT - BOTTOM_PADDING - LOGO_HEIGHT)
    wtm_logo_position = (uhh_logo_position[0] - LOGO_HEIGHT, uhh_logo_position[1])

    # Outro
    long_title_position_outro = (LEFT_PADDING, HEIGHT)
    sub_title_position_outro = (
        LEFT_PADDING, long_title_position_outro[1] + get_num_lines(long_title) * TITLE_FONTSIZE + (
            PARAGRAPH_SPACING if get_num_lines(sub_title) > 0 else 0))
    authors_position_outro = (
        LEFT_PADDING, sub_title_position_outro[1] + get_num_lines(sub_title) * STANDARD_FONTSIZE + (
            PARAGRAPH_SPACING if get_num_lines(authors) > 0 else 0))
    acknowledgement_position_outro = (
        LEFT_PADDING, authors_position_outro[1] + get_num_lines(authors) * STANDARD_FONTSIZE + (
            PARAGRAPH_SPACING if get_num_lines(acknowledgement) > 0 else 0))
    additional_information_position_outro = (LEFT_PADDING, acknowledgement_position_outro[1] + get_num_lines(
        acknowledgement) * STANDARD_FONTSIZE + (PARAGRAPH_SPACING if get_num_lines(additional_information) > 0 else 0))
    uhh_position_outro = (LEFT_PADDING, additional_information_position_outro[1] + get_num_lines(
        additional_information) * STANDARD_FONTSIZE + PARAGRAPH_SPACING)
    link_position_outro = (
        LEFT_PADDING, uhh_position_outro[1] + get_num_lines(UHH_DESCRIPTION) * STANDARD_FONTSIZE + PARAGRAPH_SPACING)
    outro_height = link_position_outro[1] + get_num_lines(INTRO_WEBSITE_LINK) * STANDARD_FONTSIZE + PARAGRAPH_SPACING
    outro_length = round(outro_height / SPEED)
    appear_time = (outro_height - (HEIGHT - BOTTOM_PADDING - LOGO_HEIGHT)) / SPEED
    text_pixel_height = authors_position[1] + get_num_lines(authors) * STANDARD_FONTSIZE + PARAGRAPH_SPACING
    if text_pixel_height > uhh_logo_position[1]:
        raise Exception(
            "Your input is too long! You need to shorten either the long title, the sub title, or the author "
            "list!")

    intro_list = []
    outro_list = []

    # Long title
    if long_title != '':
        intro_list.append(
            TextClip(long_title, font=TITLE_FONT, fontsize=TITLE_FONTSIZE, color=TITLE_FONTCOLOR, align='West',
                     kerning=8).set_position(long_title_posiiton))
        outro_list.append(
            TextClip(long_title, font=TITLE_FONT, fontsize=TITLE_FONTSIZE, color=TITLE_FONTCOLOR, align='West',
                     kerning=8).set_position(
                lambda t: (long_title_position_outro[0], int(long_title_position_outro[1] - SPEED * t))))
    # Subtitle
    if sub_title != '':
        intro_list.append(TextClip(sub_title, font=STANDARD_FONT, fontsize=STANDARD_FONTSIZE, color=STANDARD_FONTCOLOR,
                                   align='West').set_position(sub_title_position))
        outro_list.append(TextClip(sub_title, font=STANDARD_FONT, fontsize=STANDARD_FONTSIZE, color=STANDARD_FONTCOLOR,
                                   align='West').set_position(
            lambda t: (sub_title_position_outro[0], int(sub_title_position_outro[1] - SPEED * t))))

    # Authors
    if authors != '':
        intro_list.append(TextClip(authors, font=STANDARD_FONT, fontsize=STANDARD_FONTSIZE, color=STANDARD_FONTCOLOR,
                                   align='West').set_position(authors_position))
        outro_list.append(TextClip(authors, font=STANDARD_FONT, fontsize=STANDARD_FONTSIZE, color=STANDARD_FONTCOLOR,
                                   align='West').set_position(
            lambda t: (authors_position_outro[0], int(authors_position_outro[1] - SPEED * t))))

    # Acknowledgement
    if acknowledgement != '':
        outro_list.append(
            TextClip(acknowledgement, font=STANDARD_FONT, fontsize=STANDARD_FONTSIZE, color=STANDARD_FONTCOLOR,
                     align='West').set_position(
                lambda t: (acknowledgement_position_outro[0], int(acknowledgement_position_outro[1] - SPEED * t))))

    # Additional information
    if additional_information != '':
        outro_list.append(TextClip(additional_information, font=STANDARD_FONT, fontsize=STANDARD_FONTSIZE,
                                   color=STANDARD_FONTCOLOR,
                                   align='West').set_position(lambda t: (
            additional_information_position_outro[0], int(additional_information_position_outro[1] - SPEED * t))))

    # UHH description
    if UHH_DESCRIPTION != '':
        intro_list.append(
            TextClip(UHH_DESCRIPTION, font=STANDARD_FONT, fontsize=STANDARD_FONTSIZE, color=STANDARD_FONTCOLOR,
                     align='West').set_position(uhh_position))
        outro_list.append(
            TextClip(UHH_DESCRIPTION, font=STANDARD_FONT, fontsize=STANDARD_FONTSIZE, color=STANDARD_FONTCOLOR,
                     align='West').set_position(
                lambda t: (uhh_position_outro[0], int(uhh_position_outro[1] - SPEED * t))))

    # Website link
    if INTRO_WEBSITE_LINK != '':
        intro_list.append(
            TextClip(INTRO_WEBSITE_LINK, font=STANDARD_FONT, fontsize=STANDARD_FONTSIZE, color=LINK_FONTCOLOR,
                     align='West').set_position(link_position))
        outro_list.append(
            TextClip(INTRO_WEBSITE_LINK, font=STANDARD_FONT, fontsize=STANDARD_FONTSIZE, color=LINK_FONTCOLOR,
                     align='West').set_position(
                lambda t: (link_position_outro[0], int(link_position_outro[1] - SPEED * t))))

    # WTM logo
    intro_list.append(resize(ImageClip(WTM_LOGO_PATH), height=LOGO_HEIGHT).set_position(wtm_logo_position))
    outro_list.append(resize(ImageClip(WTM_LOGO_PATH), height=LOGO_HEIGHT).set_position(wtm_logo_position).set_start(
        appear_time).fadein(1))

    # UHH logo
    intro_list.append(resize(ImageClip(UHH_LOGO_PATH), height=LOGO_HEIGHT).set_position(uhh_logo_position))
    outro_list.append(resize(ImageClip(UHH_LOGO_PATH), height=LOGO_HEIGHT).set_position(uhh_logo_position).set_start(
        appear_time).fadein(1))

    # composite videos
    intro = CompositeVideoClip(intro_list, size=SCREENSIZE).set_duration(INTRO_LENGTH)
    outro = CompositeVideoClip(outro_list, size=SCREENSIZE).set_duration(outro_length)

    # main_part = TextClip("Here would be the main part of the video!", font=TITLE_FONT, fontsize=TITLE_FONTSIZE,
    #                      color=TITLE_FONTCOLOR, size=SCREENSIZE).set_duration(5)

    main_part = VideoFileClip(f"{upload_dir}/{video_id:06d}.{file_extension}").resize(newsize=SCREENSIZE)

    # outro_mov = outro.set_pos(lambda t: (0, int(100 * t)))
    final_clip = concatenate_videoclips([intro, main_part, outro])

    # Write the result to a file (many options available !)
    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass  # directory already exists

    # final_clip.write_videofile(f"{OUTPUT_DIR}test.mp4", fps=25, codec='libx264', audio_codec='aac', threads=4)

    video_path = f"{output_dir}/{video_id:06d}.mp4"
    final_clip.write_videofile(video_path, verbose=True, fps=25, codec='libx264', audio_codec='aac',
                               threads=4)

    intro.close()
    main_part.close()
    outro.close()
    final_clip.close()

    return video_path
