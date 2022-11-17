/** TRACCC library, part of the ACTS project (R&D line)
 *
 * (c) 2022 CERN for the benefit of the ACTS project
 *
 * Mozilla Public License Version 2.0
 */

#pragma once

// Project include(s).
#include "traccc/edm/cell.hpp"
#include "traccc/edm/spacepoint.hpp"
#include "traccc/utils/algorithm.hpp"
#include "traccc/utils/memory_resource.hpp"

// VecMem include(s).
#include <vecmem/utils/copy.hpp>

// System include(s).
#include <memory>

namespace traccc::cuda {

class clusterization_algorithm
    : public algorithm<spacepoint_container_types::buffer(
          const cell_container_types::const_view&)> {

    public:
    /// Constructor for clusterization algorithm
    ///
    /// @param mr is a memory resource (device)
    clusterization_algorithm(const traccc::memory_resource& mr);

    /// Callable operator for clusterization algorithm
    ///
    /// @param cells_per_event is a container with cell modules as headers
    /// and cells as the items
    /// @return a spacepoint container (buffer) - jagged vector of spacepoints
    /// per module.
    output_type operator()(
        const cell_container_types::const_view& cells_view) const override;

    private:
    traccc::memory_resource m_mr;
    std::unique_ptr<vecmem::copy> m_copy;
};

}  // namespace traccc::cuda