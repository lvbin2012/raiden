from dataclasses import replace

import pytest

from raiden.constants import EMPTY_MERKLE_ROOT
from raiden.tests.utils import factories
from raiden.transfer.mediated_transfer.state import MediationPairState
from raiden.transfer.mediated_transfer.state_change import (
    ActionInitInitiator,
    ActionInitMediator,
    ActionInitTarget,
    ReceiveTransferRefund,
    ReceiveTransferRefundCancelRoute,
)
from raiden.transfer.state import RouteState


def test_invalid_instantiation_locked_transfer_state():
    valid_unsigned = factories.create(factories.LockedTransferUnsignedStateProperties())
    valid_signed = factories.create(factories.LockedTransferSignedStateProperties())

    # neither class can be instantiated with an empty locksroot
    for valid in (valid_unsigned, valid_signed):
        empty_balance_proof = replace(valid.balance_proof, locksroot=EMPTY_MERKLE_ROOT)
        with pytest.raises(ValueError):
            replace(valid, balance_proof=empty_balance_proof)

    # an unsigned locked transfer state cannot be instantiated with a signed balance proof
    with pytest.raises(ValueError):
        replace(valid_unsigned, balance_proof=valid_signed.balance_proof)

    # and vice versa
    with pytest.raises(ValueError):
        replace(valid_signed, balance_proof=valid_unsigned.balance_proof)

    # lock is typechecked
    wrong_type_lock = object()
    for valid in (valid_unsigned, valid_signed):
        with pytest.raises(ValueError):
            replace(valid, lock=wrong_type_lock)


def test_invalid_instantiation_mediation_pair_state():
    valid = MediationPairState(
        payer_transfer=factories.create(factories.LockedTransferSignedStateProperties()),
        payee_address=factories.make_address(),
        payee_transfer=factories.create(factories.LockedTransferUnsignedStateProperties()),
    )

    unsigned_transfer = factories.create(factories.LockedTransferUnsignedStateProperties())
    with pytest.raises(ValueError):
        replace(valid, payer_transfer=unsigned_transfer)

    signed_transfer = factories.create(factories.LockedTransferSignedStateProperties())
    with pytest.raises(ValueError):
        replace(valid, payee_transfer=signed_transfer)

    hex_instead_of_binary = factories.make_checksum_address()
    with pytest.raises(ValueError):
        replace(valid, payee_address=hex_instead_of_binary)


def test_invalid_instantiation_action_init_initiator():
    wrong_type_transfer = factories.create(factories.LockedTransferSignedStateProperties())
    with pytest.raises(ValueError):
        ActionInitInitiator(transfer=wrong_type_transfer, routes=list())


@pytest.fixture
def additional_args():
    sender = factories.UNIT_TRANSFER_SENDER
    balance_proof = factories.create(factories.BalanceProofSignedStateProperties())
    return dict(sender=sender, balance_proof=balance_proof)


def test_invalid_instantiation_action_init_mediator_and_target(additional_args):
    route_state = RouteState(
        node_address=factories.make_address(),
        channel_identifier=factories.make_channel_identifier(),
    )
    not_a_route_state = object()
    valid_transfer = factories.create(factories.LockedTransferSignedStateProperties())
    wrong_type_transfer = factories.create(factories.TransferDescriptionProperties())
    routes = list()

    with pytest.raises(ValueError):
        ActionInitMediator(
            from_transfer=wrong_type_transfer,
            from_route=route_state,
            routes=routes,
            **additional_args,
        )

    with pytest.raises(ValueError):
        ActionInitMediator(
            from_transfer=valid_transfer,
            from_route=not_a_route_state,
            routes=routes,
            **additional_args,
        )

    with pytest.raises(ValueError):
        ActionInitTarget(transfer=wrong_type_transfer, route=route_state, **additional_args)

    with pytest.raises(ValueError):
        ActionInitTarget(transfer=valid_transfer, route=not_a_route_state, **additional_args)


def test_invalid_instantiation_receive_transfer_refund(additional_args):
    wrong_type_transfer = factories.create(factories.TransferDescriptionProperties())
    routes = list()
    secret = factories.UNIT_SECRET

    with pytest.raises(ValueError):
        ReceiveTransferRefund(transfer=wrong_type_transfer, routes=routes, **additional_args)

    with pytest.raises(ValueError):
        ReceiveTransferRefundCancelRoute(
            transfer=wrong_type_transfer, routes=routes, secret=secret, **additional_args
        )
