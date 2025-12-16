/**
 * TesesPage - Gestão de Teses Tributárias
 * Interface completa CRUD de teses
 */
import TeseTributariaList from '../../components/processos/TeseTributariaList';

export default function TesesPage() {
    return (
        <div className="p-6 max-w-7xl mx-auto">
            <TeseTributariaList />
        </div>
    );
}
