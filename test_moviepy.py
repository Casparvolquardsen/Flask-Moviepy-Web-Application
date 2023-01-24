from wtm_video_cutter import create_final_clip
import os

if __name__ == '__main__':
    video_path = create_final_clip(short_title="Test title",
                                   long_title="Here would be the long title and titles can be very long.",
                                   sub_title="For testing purposes, the additional description is now also very long, "
                                             "because this edge case also needs to work.",
                                   authors="Firstname1 Lastname1, Firstname2 Lastname2, Firstname3 Lastname3, "
                                           "Firstname4 Lastname4, ",
                                   additional_information="Here you have the possibility to add further information "
                                                          "which is only depicted in the outro of the video. This "
                                                          "information can be very long.",
                                   acknowledgement="The authors gratefully acknowledge the support from the Testing "
                                                   "Research Foundation TRF, project Testing",
                                   video_id=0,
                                   file_extension="mp4",
                                   upload_dir="./uploads",
                                   output_dir="./out"
                                   )

    print(f"Video is saved to the following path: {video_path}")
