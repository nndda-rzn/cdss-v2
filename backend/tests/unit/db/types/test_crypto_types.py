from cryptography.fernet import Fernet
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.encryption.fernet_provider import FernetProvider
from app.core.encryption.hash_provider import HashProvider
from app.db.base import Base
from app.db.types.context import set_crypto
from app.db.types.encrypted_string import EncryptedString
from app.db.types.hashed_string import HashedString


class _Person(Base):
    __tablename__ = "person_crypto"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(EncryptedString)
    nik_hash: Mapped[str] = mapped_column(HashedString)


def test_encrypted_roundtrip_and_hash(tmp_path):
    set_crypto(FernetProvider(Fernet.generate_key()), HashProvider(b"pepper"))
    engine = create_engine(f"sqlite:///{tmp_path / 'c.db'}")
    Base.metadata.create_all(engine, tables=[_Person.__table__])
    with Session(engine) as s:
        s.add(_Person(id=1, name="Budi", nik_hash="3171"))
        s.commit()
    with Session(engine) as s:
        p = s.scalar(select(_Person).where(_Person.id == 1))
        assert p.name == "Budi"
        assert p.nik_hash != "3171"
        assert len(p.nik_hash) == 64
