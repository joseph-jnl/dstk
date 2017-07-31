from warnings import warn
import pandas as pd
import numpy as np


def onehotencode(df, features=None, impute='retain',
                 first=True, sparse=False, tracknan=True, dropzerovar=True):
    '''
    Wrapper function for one hot encoding categorical variables

    Return modified dataframe
    '''
    dfc = df.copy()

    # Check # of categorical levels
    total_levels = sum([df[f].unique().size for f in features])
    if total_levels > 100 and not sparse:
        warn('{} categorical levels found, recommend using sparse matrix or feature selection'.format(
            total_levels))

    # Create prefix: binary#[categorical level label]
    if features:
        prefixes = ['binary#' + s for s in features]
    else:
        features = df.select_dtypes(
            include=['object', 'category']).columns
        prefixes = ['binary#' + s for s in features]

    # Impute using mode if specified
    if impute == 'mode':
        dfc[features] = dfc[features].fillna(dfc[features].mode().iloc[0])

    # One hot encode with pd.get_dummies()
    dfc = pd.get_dummies(dfc,
                         prefix=prefixes,
                         drop_first=first,
                         columns=features,
                         sparse=sparse,
                         dummy_na=tracknan)

    if impute == 'retain':
        if not tracknan:
            raise ValueError('tracknan must be True to retain nans')
        for f in features:
            flabels = [s for s in list(dfc) if s.startswith(
                'binary#' + f) and not s.endswith('_nan')]
            fnanlabel = 'binary#' + f + '_nan'
            dfc.loc[dfc[fnanlabel] == 1, flabels] = np.nan

    if dropzerovar:
        zero_var_columns = dfc.var() == 0
        dfc.drop(zero_var_columns[zero_var_columns == True].index.tolist(),
                 axis=1,
                 inplace=True)

    return dfc
