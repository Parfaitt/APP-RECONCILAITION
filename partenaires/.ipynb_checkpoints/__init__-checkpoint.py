from .cinetpay_payin import CinetpayPayinProcessor
from .cinetpay_payout import CinetpayPayoutProcessor
from .ombf_payin import OmbfPayinProcessor
from .bizao_payin import BizaoPayinProcessor
from .mtnci_payin import MtnciPayinProcessor
from .mtnci_payout import MtnciPayoutProcessor


def get_processor(file_name, data_file, partner_file):
    file_name = file_name.lower()
    
    if 'cinetpay' in file_name and 'payin' in file_name:
        return CinetpayPayinProcessor(data_file, partner_file)
    if 'cinetpay' in file_name and 'payout' in file_name:
        return CinetpayPayoutProcessor(data_file, partner_file)
    if 'ombf' in file_name and 'payin' in file_name:
        return OmbfPayinProcessor(data_file, partner_file)
    if 'bizao' in file_name and 'payin' in file_name:
        return BizaoPayinProcessor(data_file, partner_file)
    if 'mtnci' in file_name and 'payin' in file_name:
        return MtnciPayinProcessor(data_file, partner_file)

    if 'mtnci' in file_name and 'payout' in file_name:
        return MtnciPayoutProcessor(data_file, partner_file)
    
    else:
        raise ValueError("Type de partenaire non reconnu")