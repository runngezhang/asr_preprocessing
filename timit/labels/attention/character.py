#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Make label for Attention model (TIMIT corpus)."""

import os
import re
import numpy as np
from tqdm import tqdm

from prepare_path import Prepare
from utils.labels.character import char2num


# NOTE:
# 26 alphabets(a-z), SOS, EOS
# space(_), comma(,), period(.), apostorophe('), unk(@)
# = 26 + 2 + 5 = 33 labels


def read_text(label_paths, save_path=None):
    """Read text transcript.
    Args:
        label_paths: list of paths to label files
        save_path: path to save labels. If None, don't save labels
    """
    print('===> Reading target labels...')
    text_dict = {}
    char_set = set([])
    for label_path in tqdm(label_paths):
        with open(label_path, 'r') as f:
            line = f.readlines()[-1]

            # convert 「"」, 「!」, 「?」, 「:」, 「;」, 「-」 to @(<UNK>)
            # convert to lowercase
            line = re.sub(r'[\"!?:;-]+', '@', line.strip().lower())

            # convert space to "_"
            transcript = '<' + '_'.join(line.split(' ')[2:]) + '>'

        for c in list(transcript):
            char_set.add(c)

        text_dict[label_path] = transcript

    # make mapping file (from character to number)
    prep = Prepare()
    mapping_file_path = os.path.join(prep.run_root_path,
                                     'labels/attention/char2num.txt')
    char_set.discard('@')
    char_set.discard('<')
    char_set.discard('>')
    if not os.path.isfile(mapping_file_path):
        with open(mapping_file_path, 'w') as f:
            for index, char in enumerate(sorted(list(char_set))):
                f.write('%s  %s\n' % (char, str(index)))
            f.write('%s  %s\n' % ('@', str(index + 1)))
            f.write('%s  %s\n' % ('<', str(index + 2)))
            f.write('%s  %s\n' % ('>', str(index + 3)))

    if save_path is not None:
        # save target labels
        print('===> Saving target labels...')
        for label_path, transcript in tqdm(text_dict.items()):
            speaker_name = label_path.split('/')[-2]
            file_name = label_path.split('/')[-1].split('.')[0]
            save_file_name = speaker_name + '_' + file_name + '.npy'

            # convert form character to number
            char_index_list = char2num(transcript,  mapping_file_path)

            # save as npy file
            np.save(os.path.join(save_path, save_file_name), char_index_list)