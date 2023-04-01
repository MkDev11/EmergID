import uuid
import json
from typing import Dict
from web3 import Web3
import ipfshttpclient

# Connect to the Polygon network (mumbai to test)
w3 = Web3(Web3.HTTPProvider('https://rpc-mainnet.matic.network'))

# Connect to IPFS
ipfs_client = ipfshttpclient.connect('/dns/ipfs.infura.io/tcp/5001/https')

# Load the smart contract ABI
with open('SoulboundTokenABI.json', 'r') as abi_file:
    soulbound_token_abi = json.load(abi_file)

# Set the smart contract address
soulbound_token_address = '0x...'

class DIDComm:
    def create_did(self, user_data: Dict) -> str:
        user_did = f"did:example:{str(uuid.uuid4())}"
        # Save user_data and user_did to a secure database
        # You can use one of the secure database solutions mentioned in a previous response

        # Upload the user's face image to IPFS and get the IPFS hash
        image_path = user_data['image_path']
        with open(image_path, 'rb') as image_file:
            result = ipfs_client.add(image_file)
            ipfs_hash = result['Hash']

        # Mint the soulbound token
        token_uri = f"ipfs://{ipfs_hash}"
        self.mint_soulbound_token(user_did, token_uri)

    def mint_soulbound_token(self, user_did: str, token_uri: str) -> None:
        # Set the L2 address as the sender (it has the authority to mint tokens)
        l2_address = '0x...'

        # Load the SoulboundToken contract
        soulbound_token_contract = w3.eth.contract(
            address=soulbound_token_address,
            abi=soulbound_token_abi
        )

        # Mint the soulbound token
        transaction = soulbound_token_contract.functions.safeMint(user_did, token_uri).buildTransaction({
            'from': l2_address,
            'gas': 300000,
            'nonce': w3.eth.getTransactionCount(l2_address)
        })

        # Sign the transaction
        l2_private_key = '0x...'
        signed_transaction = w3.eth.account.signTransaction(transaction, l2_private_key)

        # Send the transaction
        transaction_hash = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)

        # Wait for the transaction receipt
        transaction_receipt = w3.eth.waitForTransactionReceipt(transaction_hash)

        # Check if the transaction was successful
        if transaction_receipt['status'] == 1:
            print(f"Successfully minted soulbound token for user {user_did}")
        else:
            print(f"Failed to mint soulbound token for user {user_did}")
