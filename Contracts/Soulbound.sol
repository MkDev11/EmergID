// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract SoulboundToken is ERC721URIStorage, ReentrancyGuard {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;

    address public l2Address;

    constructor(address _l2Address) ERC721("SoulboundToken", "SBT") {
        l2Address = _l2Address;
    }

    function safeMint(address to, string memory tokenURI) external {
        require(msg.sender == l2Address, "Only the L2 address can mint tokens");
        _safeMint(to, _tokenIdCounter.current());
        _setTokenURI(_tokenIdCounter.current(), tokenURI);
        _tokenIdCounter.increment();
    }
}