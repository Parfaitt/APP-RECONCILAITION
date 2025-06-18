from .cinetpay_payin import CinetpayPayinProcessor
from .cinetpay_payout import CinetpayPayoutProcessor
from .ombf_payin import OmbfPayinProcessor
from .bizao_payin import BizaoPayinProcessor
from .mtnci_payin import MtnciPayinProcessor
from .mtnci_payout import MtnciPayoutProcessor
from .waveci_payin import WaveciPayinProcessor
from .waveci_payout import WaveciPayoutProcessor
from .ifutur_payin import ifuturPayinProcessor
from .mtncm_payin import MtncmPayinProcessor
from .mtncm_payout import MtncmPayoutProcessor
from .ifutur_payout import IfuturPayoutProcessor
from .omci_payout import OmciPayoutProcessor
from .omci_payin import OmciPayinProcessor
from .moovci_payin import MoovciPayinProcessor

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
    if 'waveci' in file_name and 'payin' in file_name:
        return WaveciPayinProcessor(data_file, partner_file)
    if 'waveci' in file_name and 'payout' in file_name:
        return WaveciPayoutProcessor(data_file, partner_file)
    if 'ifutur' in file_name and 'payin' in file_name:
        return ifuturPayinProcessor(data_file, partner_file)
    if 'mtncm' in file_name and 'payin' in file_name:
        return MtncmPayinProcessor(data_file, partner_file)
    if 'mtncm' in file_name and 'payout' in file_name:
        return MtncmPayoutProcessor(data_file, partner_file)
    if 'ifutur' in file_name and 'payout' in file_name:
        return IfuturPayoutProcessor(data_file, partner_file)
    if 'omci' in file_name and 'payout' in file_name:
        return OmciPayoutProcessor(data_file, partner_file)
    if 'omci' in file_name and 'payin' in file_name:
        return OmciPayinProcessor(data_file, partner_file)
    if 'moovci' in file_name and 'payin' in file_name:
        return MoovciPayinProcessor(data_file, partner_file)
    
    else:
        raise ValueError("Type de partenaire non reconnu")